"""Source-first pilot inventory. No crawling, raw edits, public exports or auto-publish."""

from collections import Counter
import hashlib
import json
from pathlib import Path

from .core import Registry, RegistryError, canonical, inspect_file, safe_path, sha256_file


LEGACY = 'data-pipeline/01_raw/factory_cost_registry.json'
PREPARED = 'data-pipeline/02_prepared/factory_costs.json'
MEDIA = 'public/data/catalog_media.json'
RAW = 'data-pipeline/01_raw/08_factory_costs/'
GENERATOR = 'smartgift.knowledge-registry.frozen-plan/1'


def _read(root, path):
    return json.loads(safe_path(root, path, source=True).read_text(encoding='utf-8'))


def _digest(plan):
    return hashlib.sha256(canonical({k: v for k, v in plan.items() if k != 'plan_sha256'}).encode()).hexdigest()


def build_plan(workspace_root):
    root = Path(workspace_root).resolve()
    assets = {}
    def add(path, kind='Document', origin=None, expected=None, visual_origin='unknown'):
        info = inspect_file(root, path, kind, expected)
        record = dict(info, kind=kind, origin_key=origin or 'local:' + info['path'],
                      classification='product_metadata', visual_origin=visual_origin)
        if path in assets and assets[path] != record:
            raise RegistryError('Conflicting asset classifications')
        assets[path] = record
        return record
    for path in (LEGACY, PREPARED, MEDIA):
        add(path)
    legacy, prepared, media = (_read(root, p) for p in (LEGACY, PREPARED, MEDIA))
    rows = prepared['records']
    observed = Counter(row['source_file'] for row in rows)
    if set(observed) != set(prepared['metadata']['sources']) or set(observed) != set(legacy['files']):
        raise RegistryError('Prepared/legacy source coverage mismatch; review changed inventory')
    source_bindings = {}
    archive_count = 0
    for name, source in sorted(prepared['metadata']['sources'].items()):
        if '/' in name or '\\' in name or source['records_extracted'] != observed[name]:
            raise RegistryError('Unsafe filename or source record-count mismatch')
        entry = legacy['files'][name]
        if source['sha256'] != entry['current_sha256']:
            raise RegistryError('Prepared source does not match current legacy version')
        origin = 'legacy:factory_costs:' + name
        add(RAW + name, origin=origin, expected=source['sha256'])
        histories = entry['history']
        if not any(h['sha256'] == source['sha256'] for h in histories):
            raise RegistryError('Missing legacy version')
        for history in histories:
            if not history['archive_path'].startswith('data-pipeline/01_raw/archive/factory_costs/'):
                raise RegistryError('Archive outside approved source lane')
            add(history['archive_path'], origin=origin, expected=history['sha256'])
            archive_count += 1
        source_bindings[name] = {'path': RAW + name, 'records': observed[name],
                                 'legacy_version_ids': [h['version_id'] for h in histories]}
    missing = sum(row.get('exw_price') is None for row in rows)
    if (len(rows) != prepared['metadata']['total_records'] or
            len(rows) - missing != prepared['metadata']['records_with_price']):
        raise RegistryError('Prepared record/price counts inconsistent')
    refs = []
    entries = ([('/hero', media['hero'])] if media.get('hero') else [])
    for group in ('sets', 'products'):
        entries.extend((f'/{group}/{i}', item) for i, item in enumerate(media.get(group, [])))
    origins = {}
    for pointer, item in entries:
        url = item['image']
        if not isinstance(url, str) or not url.startswith('/assets/catalog-media/'):
            raise RegistryError('Media outside approved local catalog image lane')
        path = 'public' + url
        # Existing generated flags are preserved as claims, not physical-product proof.
        origin = 'generated' if item.get('generated_from_catalog') is True else 'unknown'
        origins.setdefault(path, set()).add(origin)
        refs.append({'owner_path': MEDIA, 'target_path': path, 'locator': {'kind': 'json', 'pointer': pointer},
                     'visual_origin_claim': origin, 'identity_status': 'unresolved', 'usage_rights': 'unknown'})
    for path, claims in sorted(origins.items()):
        add(path, 'Picture', visual_origin=next(iter(claims)) if len(claims) == 1 else 'unknown')
    plan = {'generator': GENERATOR, 'scope': ['Org-EtohGroup', 'SmartGift'],
            'contract_sha256': Registry(root).contract_hash, 'status': 'awaiting_manifest_review',
            'publish_authorized': False, 'assets': [assets[key] for key in sorted(assets)],
            'source_bindings': source_bindings, 'attachments': refs,
            'coverage': {'physical_files': len(assets), 'factory_documents': len(source_bindings),
                         'archive_locations': archive_count, 'cost_records': len(rows),
                         'priced_records': len(rows)-missing, 'missing_price_records': missing,
                         'prepared_record_only': len(rows), 'raw_cell_exact': 0,
                         'picture_files': len(origins), 'attachment_occurrences': len(refs),
                         'visual_origin_conflicts': sum(len(v)>1 for v in origins.values()),
                         'unique_content_hashes': len({v['sha256'] for v in assets.values()})},
            'excluded_scope': ['CRM/customer sources (not enumerated)', 'unclassified workspace sources',
                               'external media/URLs', 'new OCR/embeddings', 'exact PDF/Excel recovery (P3 pending)']}
    plan['plan_sha256'] = _digest(plan)
    verify_plan(root, plan)
    return plan


def verify_plan(workspace_root, plan):
    root = Path(workspace_root).resolve()
    if (plan.get('generator') != GENERATOR or plan.get('scope') != ['Org-EtohGroup', 'SmartGift']
            or plan.get('plan_sha256') != _digest(plan) or
            plan.get('contract_sha256') != Registry(root).contract_hash):
        raise RegistryError('Frozen plan ownership/hash/contract mismatch')
    for asset in plan['assets']:
        info = inspect_file(root, asset['path'], asset['kind'], asset['sha256'])
        if info['size_bytes'] != asset['size_bytes'] or info['detected_mime'] != asset['detected_mime']:
            raise RegistryError('Frozen source metadata mismatch')
    return True


def stage_plan(workspace_root, plan):
    """Build proposed records in memory; never writes ledger/CURRENT or a vault."""
    root = Path(workspace_root).resolve()
    verify_plan(root, plan)
    # Rebuild to check semantic fields too; a checksum is not an approval/signature.
    if build_plan(root) != plan:
        raise RegistryError('Frozen plan differs from current classified inventory')
    registry, versions = Registry(root), {}
    for asset in plan['assets']:
        _, versions[asset['path']] = registry.register_asset(
            asset['path'], kind=asset['kind'], origin_key=asset['origin_key'],
            expected_sha256=asset['sha256'], classification=asset['classification'], visual_origin=asset['visual_origin'])
    sources = {}
    for name, binding in plan['source_bindings'].items():
        sources[name] = registry.evidence(versions[binding['path']], {'kind': 'file'},
                                          record_kind='factory_source', locator_status='file_only')
    for index, row in enumerate(_read(root, PREPARED)['records']):
        evidence = registry.evidence(versions[PREPARED], {'kind': 'json', 'pointer': f'/records/{index}'},
                                     record_kind='factory_cost', locator_status='prepared_record_only')
        registry.link('DEPENDS_ON', evidence, sources[row['source_file']])
    for attachment in plan['attachments']:
        registry.attach(versions[attachment['owner_path']], versions[attachment['target_path']], attachment['locator'])
    registry.validate()
    registry._check_inputs()
    return registry
