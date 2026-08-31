"""Rebuildable Genesis projection; ledger remains the only registration writer."""

import json
import os
from pathlib import Path
import subprocess
import tempfile

from .core import Registry, RegistryError, canonical, safe_path, sha256_file, uuid7


VAULT = 'vaults/vlt-knowledge-registry/genesis-db'
WORKER = Path(__file__).with_name('genesis_worker.cjs')


def _database_hashes(directory):
    if not directory.is_dir():
        raise RegistryError('Projection database unavailable')
    files = {}
    for path in sorted(directory.rglob('*')):
        if not path.resolve().is_relative_to(directory.resolve()):
            raise RegistryError('Projection file escapes database directory')
        if path.is_file():
            files[path.relative_to(directory).as_posix()] = sha256_file(path)
    if not files:
        raise RegistryError('Projection database is empty')
    return files


def _worker(mode, payload, database, node):
    result = subprocess.run([node, str(WORKER), mode, str(payload), str(database)],
                            capture_output=True, text=True, encoding='utf-8', timeout=60,
                            cwd=WORKER.parents[2])
    if result.returncode:
        raise RegistryError('Native projection failed; current pointer unchanged: ' + result.stderr[-1500:])
    lines = [line[7:] for line in result.stdout.splitlines() if line.startswith('RESULT:')]
    if len(lines) != 1:
        raise RegistryError('Native projection did not acknowledge completion')
    return json.loads(lines[0])


def project(workspace_root, node='node'):
    registry = Registry(workspace_root)
    if registry.generation_id is None:
        raise RegistryError('Cannot project an unpublished registry')
    with registry._writer():
        registry.validate()
        generation = registry.generation_id
        directory = safe_path(registry.root, f'{VAULT}/projections/proj-{uuid7()}')
        directory.mkdir(parents=True, exist_ok=False)
        payload = directory / 'input.json'
        payload.write_text(canonical({'generation_id': generation, 'nodes': list(registry.nodes.values()),
                                       'edges': list(registry.edges.values())}), encoding='utf-8')
        database = directory / 'db'
        _worker('write', payload, database, node)
        verified = _worker('verify', payload, database, node)
        descriptor = {'generator': 'smartgift.knowledge-registry.projection/1', 'generation_id': generation,
                      'contract_sha256': registry.contract_hash, 'node_count': len(registry.nodes),
                      'edge_count': len(registry.edges), 'native_readback_verified': verified['verified'],
                      'database_path': database.relative_to(registry.root).as_posix(),
                      'database_checksums': _database_hashes(database),
                      'payload_sha256': sha256_file(payload)}
        (directory/'manifest.json').write_text(canonical(descriptor), encoding='utf-8')
        pointer = safe_path(registry.root, f'{VAULT}/CURRENT')
        with tempfile.NamedTemporaryFile(dir=pointer.parent, prefix='.CURRENT-', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write((directory.name + '\n').encode())
            stream.flush()
            os.fsync(stream.fileno())
        try:
            if registry._current() != generation:
                raise RegistryError('Ledger changed while projecting')
            os.replace(temporary, pointer)
        finally:
            temporary.unlink(missing_ok=True)
        return descriptor


def projection_status(workspace_root):
    registry = Registry(workspace_root)
    pointer = safe_path(registry.root, f'{VAULT}/CURRENT')
    if not pointer.exists():
        return {'status': 'unavailable', 'generation_id': registry.generation_id}
    name = pointer.read_text(encoding='utf-8').strip()
    import re
    if not re.fullmatch(r'proj-[0-9a-f-]{36}', name):
        raise RegistryError('Invalid graph pointer')
    directory = safe_path(registry.root, f'{VAULT}/projections/{name}')
    descriptor = json.loads((directory/'manifest.json').read_text(encoding='utf-8'))
    if (descriptor.get('generator') != 'smartgift.knowledge-registry.projection/1'
            or descriptor.get('contract_sha256') != registry.contract_hash
            or descriptor.get('database_path') != (directory/'db').relative_to(registry.root).as_posix()
            or sha256_file(directory/'input.json') != descriptor.get('payload_sha256')):
        raise RegistryError('Projection ownership/contract/input mismatch')
    if _database_hashes(directory/'db') != descriptor.get('database_checksums'):
        raise RegistryError('Projection database checksum mismatch')
    status = 'current' if descriptor['generation_id'] == registry.generation_id else 'stale'
    return dict(descriptor, status=status)
