"""ADR-007 registry behavior; fixtures contain synthetic product metadata only."""

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from uuid import UUID

from pipeline.knowledge_registry import Registry, RegistryError, sha256_file


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="knowledge-registry-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "sources").mkdir()
        self.source = self.root / "sources/book.json"
        self.source.write_text('{"records":[{"code":"TEST-1","cost":null}]}', encoding="utf-8")
        self.registry = Registry(self.root)

    def asset(self, path="sources/book.json", **kwargs):
        return self.registry.register_asset(path, **kwargs)

    def test_document_uuid7_and_repeat_are_stable(self):
        first = self.asset()
        self.assertEqual(first, self.asset())
        self.assertEqual(7, UUID(first[0].split(":", 1)[1]).version)
        self.assertTrue(first[0].startswith("doc:"))
        self.assertEqual(3, len(self.registry.nodes))

    def test_new_bytes_keep_asset_and_add_version(self):
        old = self.asset()
        self.source.write_text('{"changed":true}', encoding="utf-8")
        new = self.asset()
        self.assertEqual(old[0], new[0])
        self.assertNotEqual(old[1], new[1])
        self.assertEqual(2, self.registry.nodes[new[1]]["props"]["ordinal"])

    def test_duplicates_do_not_merge_origins_but_archive_alias_can_share_version(self):
        first = self.asset(origin_key="legacy:one")
        (self.root / "sources/copy.json").write_bytes(self.source.read_bytes())
        other = self.asset("sources/copy.json")
        self.assertNotEqual(first[0], other[0])
        same = self.asset("sources/copy.json", origin_key="legacy:one")
        self.assertEqual(first, same)

    def test_picture_and_media_types_and_attachments(self):
        (self.root / "sources/pic.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"test")
        (self.root / "sources/sound.wav").write_bytes(b"RIFF" + b"\0"*4 + b"WAVE" + b"test")
        doc, version = self.asset()
        pic, pic_version = self.asset("sources/pic.png", kind="Picture")
        media, _ = self.asset("sources/sound.wav", kind="Media")
        self.assertTrue(pic.startswith("pic:"))
        self.assertTrue(media.startswith("media:"))
        a = self.registry.attach(version, pic_version, {"kind":"json", "pointer":"/records/0"})
        b = self.registry.attach(version, pic_version, {"kind":"json", "pointer":"/records/1"})
        self.assertNotEqual(a, b)
        self.assertTrue(a.startswith("att:"))
        self.assertEqual(a, self.registry.attach(version, pic_version, {"kind":"json", "pointer":"/records/0"}))
        self.assertIn(doc, self.registry.trace_origin(pic)["node_ids"])

    def test_evidence_keeps_missing_price_and_partial_locator(self):
        _, version = self.asset()
        ev = self.registry.evidence(version, {"kind":"json", "pointer":"/records/0"},
                                     record_kind="factory_cost", locator_status="prepared_record_only")
        self.assertEqual(ev, self.registry.evidence(version, {"kind":"json", "pointer":"/records/0"},
                                                    record_kind="factory_cost", locator_status="prepared_record_only"))
        self.assertEqual("prepared_record_only", self.registry.nodes[ev]["props"]["locator_status"])
        self.assertIn(version, self.registry.trace_origin(ev)["node_ids"])

    def test_reject_unknown_classification_and_customer_path(self):
        for classification in ("unknown", "customer", "public"):
            with self.assertRaises(RegistryError):
                self.asset(classification=classification)
        for path in ("sources/company_contact.xlsx", "data-pipeline/01_raw/05_crm_customer_data/a.json"):
            with self.assertRaises(RegistryError):
                self.asset(path)
        self.assertEqual({}, self.registry.nodes)

    def test_reject_escape_missing_hash_mismatch_and_type_mismatch_before_mutation(self):
        for path, kwargs in (("../escape.json", {}), ("C:/outside.json", {}), ("sources/missing.json", {}),
                             ("sources/book.json", {"expected_sha256":"0"*64}),
                             ("sources/book.json", {"kind":"Picture"})):
            with self.assertRaises(RegistryError):
                self.asset(path, **kwargs)
        self.assertEqual({}, self.registry.nodes)

    def test_reject_symlink_escape(self):
        with tempfile.TemporaryDirectory() as other:
            target = Path(other) / "outside.json"
            target.write_text("{}")
            link = self.root / "sources/link.json"
            try:
                link.symlink_to(target)
            except OSError:
                self.skipTest("OS does not allow creating symlinks")
            with self.assertRaises(RegistryError):
                self.asset("sources/link.json")

    def test_invalid_edges_cycles_and_locators_fail(self):
        doc, version = self.asset()
        for rel, a, b in (("NOPE",doc,version), ("HAS_VERSION",version,doc),
                           ("HAS_VERSION",doc,"missing"), ("DERIVED_FROM",version,version)):
            with self.assertRaises(RegistryError):
                self.registry.link(rel,a,b)
        self.source.write_text('{"v":2}')
        _, second = self.asset()
        self.registry.link("DERIVED_FROM",second,version)
        with self.assertRaises(RegistryError):
            self.registry.link("DERIVED_FROM",version,second)
        for locator in ({"kind":"spreadsheet","sheet_name":"Sheet1","row_number":0,"cell_ref":"A0"},
                        {"kind":"pdf","page_number":-1}, {"kind":"media_time","time_start_ms":10,"time_end_ms":2},
                        {"kind":"json","pointer":"not-a-pointer"}):
            with self.assertRaises(RegistryError):
                self.registry.evidence(version,locator)

    def test_bounds_scope_and_truncation(self):
        doc, version = self.asset()
        with self.assertRaises(RegistryError):
            self.registry.trace_origin(doc, depth=7)
        with self.assertRaises(RegistryError):
            self.registry.trace_origin(doc, scope=("other","SmartGift"))
        result = self.registry.trace_origin(doc, max_nodes=1)
        self.assertTrue(result["truncated"])
        self.assertEqual("node_limit",result["reason"])
        self.assertEqual([doc],result["node_ids"])
        self.registry.nodes[version]["business_id"] = "other"
        with self.assertRaises(RegistryError):
            self.registry.trace_origin(doc)

    def test_pagination_bound_to_owner_and_generation(self):
        _, version = self.asset()
        for n in range(3):
            self.registry.attach(version, version, {"kind":"json", "pointer":f"/records/{n}"})
        page1 = self.registry.list_attachments(version, limit=2)
        self.assertEqual(2,len(page1["items"]))
        page2 = self.registry.list_attachments(version, limit=2, cursor=page1["next_cursor"])
        self.assertEqual(1,len(page2["items"]))
        self.assertIsNone(page2["next_cursor"])
        with self.assertRaises(RegistryError):
            self.registry.list_attachments(version,limit=101)

    def test_commit_reload_noop_and_rollback(self):
        first = self.asset()
        gen1 = self.registry.commit()
        loaded = Registry(self.root)
        self.assertEqual(first,loaded.register_asset("sources/book.json"))
        self.assertEqual(gen1,loaded.commit())
        self.source.write_text('{"next":1}')
        loaded.register_asset("sources/book.json")
        gen2 = loaded.commit()
        self.assertNotEqual(gen1,gen2)
        loaded.rollback(gen1)
        self.assertEqual(gen1,Registry(self.root).generation_id)

    def test_concurrent_writer_and_failed_publish_preserve_current(self):
        stale = Registry(self.root)
        self.asset()
        first = self.registry.commit()
        stale.register_asset("sources/book.json")
        with self.assertRaises(RegistryError):
            stale.commit()
        self.source.write_text('{"next":1}')
        self.asset()
        with patch("pipeline.knowledge_registry.core.os.replace",side_effect=OSError("simulated crash")):
            with self.assertRaises(OSError):
                self.registry.commit()
        self.assertEqual(first,Registry(self.root).generation_id)

    def test_lock_and_tampered_generation_fail_closed(self):
        self.asset()
        gen = self.registry.commit()
        store = self.root / "data-pipeline/00_knowledge_registry"
        (store/"WRITER.lock").write_text("another writer")
        with self.assertRaises(RegistryError):
            self.registry.commit()
        (store/"WRITER.lock").unlink()
        nodes = store / "generations" / gen / "nodes.jsonl"
        nodes.write_text("{}\n")
        with self.assertRaises(RegistryError):
            Registry(self.root)

    def test_source_mutation_before_publish_preserves_current(self):
        self.asset()
        first = self.registry.commit()
        self.source.write_text('{"v":2}')
        self.asset()
        self.source.write_text('{"v":3}')
        with self.assertRaisesRegex(RegistryError, "Input changed"):
            self.registry.commit()
        self.assertEqual(first, Registry(self.root).generation_id)

    def test_noop_still_checks_inputs(self):
        self.asset()
        self.registry.commit()
        self.source.write_text('{"changed":true}')
        with self.assertRaisesRegex(RegistryError, "Input changed"):
            self.registry.commit()

    def test_complete_relationships_and_metadata_are_validated(self):
        doc, version = self.asset()
        edge = next(k for k,v in self.registry.edges.items() if v['rel'] == 'HAS_VERSION')
        del self.registry.edges[edge]
        with self.assertRaises(RegistryError):
            self.registry.commit()
        self.registry.link('HAS_VERSION', doc, version)
        self.registry.nodes[doc]['props']['customer_contact'] = 'synthetic-forbidden'
        with self.assertRaises(RegistryError):
            self.registry.commit()

    def test_audit_intent_is_hash_chained_and_noop_does_not_append(self):
        self.asset()
        self.registry.commit()
        audit = self.root / 'data-pipeline/00_knowledge_registry/audit/events.jsonl'
        first = audit.read_bytes()
        self.registry.commit()
        self.assertEqual(first, audit.read_bytes())
        self.source.write_text('{"v":2}')
        self.asset()
        self.registry.commit()
        entries = [json.loads(line) for line in audit.read_text().splitlines()]
        self.assertEqual(2, len(entries))
        self.assertEqual(entries[0]['sha256'], entries[1]['previous_sha256'])

    def test_missing_common_metadata_fails_closed(self):
        doc, _ = self.asset()
        del self.registry.nodes[doc]['registry_contract_version']
        with self.assertRaises(RegistryError):
            self.registry.commit()

    def test_rollback_cannot_activate_an_unpublished_candidate(self):
        self.asset()
        current = self.registry.commit()
        self.source.write_text('{"v":2}')
        self.asset()
        with patch('pipeline.knowledge_registry.core.os.replace', side_effect=OSError('crash')):
            with self.assertRaises(OSError):
                self.registry.commit()
        generations = self.root/'data-pipeline/00_knowledge_registry/generations'
        orphan = next(p.name for p in generations.iterdir() if p.name != current)
        with self.assertRaises(RegistryError):
            self.registry.rollback(orphan)


if __name__ == "__main__":
    unittest.main()
