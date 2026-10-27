"""Я проверяю денежно-независимый контракт, blocking checks и реальные сбои публикации."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from delivery_assets.domain import ContractError,MAX_BYTES,canonical,fixture,parse_csv,parse_day,quality,summarize
from delivery_assets.storage import latest,locked,prepare,publish

class DomainTests(unittest.TestCase):
    def test_expected_totals_and_future_not_delivered(self):
        report=summarize(parse_csv(fixture()),'2026-10-26')
        self.assertEqual(report['totals'],{'due_count':5,'on_time':2,'late':1,'overdue':2})
        self.assertEqual(report['warehouses'][0]['max_known_late_seconds'],1200)
        self.assertEqual(report['warehouses'][1]['overdue'],1)
    def test_empty_is_explicit_header(self):
        header=fixture().splitlines(keepends=True)[0];report=summarize(parse_csv(header),'2026-10-26')
        self.assertEqual(report['totals']['due_count'],0)
        with self.assertRaises(ContractError):parse_csv(b'')
    def test_broken_input_rejected(self):
        for raw in (b'a,b\n1,2\n',fixture().replace(b'WH-A',b'WH-X'),fixture().replace(b'08:59:00Z',b'08:59:00'),fixture().replace(b'D001',b'Person'),b'x'*(MAX_BYTES+1),fixture().replace(b',2026-10-26T08:59:00Z',b'')):
            with self.subTest(raw=raw[:20]),self.assertRaises(ContractError):parse_csv(raw)
    def test_quality_properties_independent(self):
        self.assertEqual(quality(parse_csv(fixture('duplicate'))),{'unique_delivery_ids':1,'consistent_chronology':0})
        self.assertEqual(quality(parse_csv(fixture('chronology'))),{'unique_delivery_ids':0,'consistent_chronology':1})
    def test_identity_is_repeatable_and_changed_bytes_new(self):
        baseline=summarize(parse_csv(fixture()),'2026-10-26')
        self.assertEqual(baseline,summarize(parse_csv(fixture()),'2026-10-26'))
        self.assertNotEqual(baseline['request_id'],summarize(parse_csv(fixture('revised')),'2026-10-26')['request_id'])
    def test_day_canonical_and_bounded(self):
        for value in ('2026-W44-1','0000-01-01','2019-01-01','2100-01-01','2026-02-30'):
            with self.subTest(value=value),self.assertRaises(ContractError):parse_day(value)
    def test_exclusive_day_end_boundary(self):
        at_cutoff=fixture().replace(b'2026-10-27T00:10:00Z',b'2026-10-27T00:00:00Z')
        before=fixture().replace(b'2026-10-27T00:10:00Z',b'2026-10-26T23:59:59Z')
        self.assertEqual(summarize(parse_csv(at_cutoff),'2026-10-26')['totals']['overdue'],2)
        self.assertEqual(summarize(parse_csv(before),'2026-10-26')['totals']['overdue'],1)
    def test_other_day_not_selected(self):
        self.assertEqual(summarize(parse_csv(fixture()),'2026-10-25')['totals']['due_count'],1)

class StorageTests(unittest.TestCase):
    def test_unowned_workspace_and_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);(folder/'foreign').write_text('keep',encoding='utf-8')
            with self.assertRaises(ContractError):prepare(folder)
            root=prepare(folder/'ours')
            with locked(root):
                with self.assertRaises(ContractError):
                    with locked(root):pass
    def test_failure_keeps_old_pointer_and_resume_reuses_object(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=prepare(Path(tmp)/'state');a=summarize(parse_csv(fixture()),'2026-10-26');b=summarize(parse_csv(fixture('revised')),'2026-10-26')
            publish(root/'published',a);pointer=(root/'published/latest.json').read_bytes()
            with self.assertRaises(ContractError):publish(root/'published',b,True)
            self.assertEqual((root/'published/latest.json').read_bytes(),pointer)
            self.assertTrue(publish(root/'published',b)['reused_object'])
            self.assertEqual(latest(root),b)
            self.assertEqual((root/'published/objects'/(a['request_id']+'.json')).read_bytes(),canonical(a))
    def test_corrupt_pointer_shape_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=prepare(Path(tmp)/'state');report=summarize(parse_csv(fixture()),'2026-10-26');publish(root/'published',report)
            for raw in (b'[]',b'null',b'{"request_id":"../../escape","sha256":"bad"}'):
                (root/'published/latest.json').write_bytes(raw)
                with self.assertRaises(ContractError):latest(root)
    def test_object_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=prepare(Path(tmp)/'state');report=summarize(parse_csv(fixture()),'2026-10-26');publish(root/'published',report)
            (root/'published/objects'/(report['request_id']+'.json')).write_bytes(b'{}')
            with self.assertRaises(ContractError):latest(root)
            with self.assertRaises(ContractError):publish(root/'published',report)

class DagsterTests(unittest.TestCase):
    def test_real_blocking_chronology_and_recovery(self):
        from delivery_assets.__main__ import demo
        from delivery_assets.pipeline import run,history
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'demo';result=demo(root)
            self.assertEqual(result['objects'],2)
            self.assertEqual(result['runs'][2]['materialized'],['raw_deliveries'])
            self.assertEqual(result['runs'][3]['materialized'],['raw_deliveries','delivery_summary'])
            self.assertEqual(result['latest']['warehouses'][0]['max_known_late_seconds'],300)
            self.assertEqual(sum(r['status']=='FAILURE' for r in result['history']),2)
            bad=root/'bad.csv';bad.write_bytes(fixture('chronology'));failed=run(bad,'2026-10-26',root/'state')
            self.assertFalse(failed['success']);self.assertEqual(failed['materialized'],['raw_deliveries'])
            self.assertEqual(len(history(root/'state')),6)
    def test_parse_failure_has_no_materializations(self):
        from delivery_assets.pipeline import run
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);path=root/'bad.csv';path.write_bytes(b'wrong')
            result=run(path,'2026-10-26',root/'state');self.assertFalse(result['success']);self.assertEqual(result['materialized'],[])
