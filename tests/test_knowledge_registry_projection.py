"""Real Genesis projection is isolated from production/customer stores."""

import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from pipeline.knowledge_registry import Registry, RegistryError
from pipeline.knowledge_registry.projection import project, projection_status


@unittest.skipUnless(shutil.which('node'), 'Node required for native capability')
class ProjectionTests(unittest.TestCase):
    def test_pilot_sized_fanout_is_verified_without_truncating_records(self):
        root_base = Path(__file__).resolve().parents[1] / 'tmp'
        root_base.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='knowledge-registry-projection-', dir=root_base) as directory:
            root = Path(directory)
            (root/'source.json').write_text(json.dumps({'records': [None]*1166}))
            registry = Registry(root)
            _, version = registry.register_asset('source.json')
            for i in range(1166):
                registry.evidence(version, {'kind': 'json', 'pointer': f'/records/{i}'},
                                  record_kind='factory_cost', locator_status='prepared_record_only')
            registry.commit()
            self.assertEqual(1169, project(root)['node_count'])

    def test_projection_persists_and_detects_stale_generation(self):
        root_base = Path(__file__).resolve().parents[1] / 'tmp'
        root_base.mkdir(exist_ok=True)
        # Native workers exit before fixture cleanup; no live database handles.
        with tempfile.TemporaryDirectory(prefix='knowledge-registry-projection-', dir=root_base) as directory:
            root = Path(directory)
            (root/'source.json').write_text('{}')
            registry = Registry(root)
            doc, version = registry.register_asset('source.json')
            registry.commit()
            result = project(root)
            self.assertEqual(registry.generation_id, result['generation_id'])
            self.assertEqual('current', projection_status(root)['status'])
            self.assertEqual(3, result['node_count'])
            self.assertEqual(2, result['edge_count'])
            self.assertTrue(result['native_readback_verified'])
            (root/'source.json').write_text('{"v":2}')
            registry.register_asset('source.json')
            registry.commit()
            self.assertEqual('stale', projection_status(root)['status'])
            with patch('pipeline.knowledge_registry.projection.os.replace', side_effect=OSError('simulated crash')):
                with self.assertRaises(OSError):
                    project(root)
            self.assertEqual(result['generation_id'], projection_status(root)['generation_id'])
            project(root)
            registry.rollback(result['generation_id'])
            self.assertEqual('stale', projection_status(root)['status'])
            project(root)
            self.assertEqual('current', projection_status(root)['status'])
            current_projection = projection_status(root)
            database = root/current_projection['database_path']
            source_file = next(p for p in database.rglob('*') if p.is_file())
            source_file.write_bytes(b'tampered synthetic database')
            with self.assertRaises(RegistryError):
                projection_status(root)

    def test_unpublished_registry_cannot_be_projected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(RegistryError):
                project(Path(directory))


if __name__ == '__main__':
    unittest.main()
