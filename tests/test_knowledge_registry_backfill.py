"""Frozen plans do not publish IDs; synthetic cost records are not SRP-filtered."""

import json
from pathlib import Path
import tempfile
import unittest

from pipeline.knowledge_registry import Registry, RegistryError, sha256_file
from pipeline.knowledge_registry.backfill import build_plan, verify_plan, stage_plan


class BackfillTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='knowledge-registry-plan-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.raw = 'data-pipeline/01_raw/08_factory_costs/test.xlsx'
        self.archive = 'data-pipeline/01_raw/archive/factory_costs/test.xlsx'
        for path in (self.raw, self.archive):
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b'PK\x03\x04synthetic fixture')
        self.digest = sha256_file(self.root / self.raw)
        self.write('data-pipeline/01_raw/factory_cost_registry.json', {'files': {'test.xlsx': {
            'current_sha256': self.digest, 'history': [{'sha256': self.digest,
            'version_id': 'legacy-v1', 'archive_path': self.archive}]}}})
        self.write('data-pipeline/02_prepared/factory_costs.json', {
            'metadata': {'total_records': 2, 'records_with_price': 1, 'sources': {'test.xlsx': {
                'sha256': self.digest, 'records_extracted': 2}}},
            'records': [{'source_file': 'test.xlsx', 'exw_price': 12},
                        {'source_file': 'test.xlsx', 'exw_price': None}]})
        self.write('public/data/catalog_media.json', {'hero': None, 'sets': [], 'products': []})

    def write(self, path, data):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(data), encoding='utf-8')

    def test_source_first_dry_run_is_deterministic_and_does_not_publish(self):
        plan = build_plan(self.root)
        self.assertEqual(plan, build_plan(self.root))
        self.assertEqual(2, plan['coverage']['cost_records'])
        self.assertEqual(1, plan['coverage']['missing_price_records'])
        self.assertEqual(1, plan['coverage']['factory_documents'])
        self.assertFalse((self.root/'data-pipeline/00_knowledge_registry').exists())
        staged = stage_plan(self.root, plan)
        self.assertEqual(2, sum(n['type']=='EvidenceRecord' and n['props']['record_kind']=='factory_cost'
                                for n in staged.nodes.values()))
        self.assertEqual(4, sum(n['type']=='Document' for n in staged.nodes.values()))
        self.assertFalse((self.root/'data-pipeline/00_knowledge_registry').exists())

    def test_plan_detects_source_changes_and_tampering(self):
        plan = build_plan(self.root)
        (self.root/self.raw).write_bytes(b'PK\x03\x04changed')
        with self.assertRaises(RegistryError):
            verify_plan(self.root, plan)
        plan['coverage']['cost_records'] = 9
        with self.assertRaises(RegistryError):
            stage_plan(self.root, plan)

    def test_missing_and_unknown_source_are_blocked_not_silently_dropped(self):
        (self.root/self.archive).unlink()
        with self.assertRaises(RegistryError):
            build_plan(self.root)


if __name__ == '__main__':
    unittest.main()
