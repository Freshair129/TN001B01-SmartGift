"""Immutable generations with a single-writer, compare-and-swap CURRENT pointer.

This is a local metadata boundary, not an authentication service or a PII detector.
Callers must classify sources before registration. Raw content is never persisted.
"""

from collections import defaultdict, deque
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import itertools
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import secrets
import tempfile
import time
from uuid import UUID

import yaml


class RegistryError(ValueError):
    pass


SCHEMA = Path(__file__).resolve().parents[2] / "config/schema_genesisblock.yaml"
GENERATOR = "smartgift.knowledge-registry/1"
SCOPE = ("Org-EtohGroup", "SmartGift")
ACCESS = "smartgift:internal:product-metadata"
STORE = "data-pipeline/00_knowledge_registry"
DENIED = re.compile(r"05_crm_customer_data|customer|contact|quotation|ลูกค้า|ใบเสนอราคา", re.I)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def uuid7():
    bits = ((time.time_ns() // 1_000_000) << 80) | (7 << 76)
    bits |= secrets.randbits(12) << 64 | (2 << 62) | secrets.randbits(62)
    return str(UUID(int=bits))


def now():
    return datetime.now(timezone.utc).isoformat()


def safe_path(root, relative, *, source=False):
    if not isinstance(relative, str) or not relative or "\x00" in relative:
        raise RegistryError("Invalid relative path")
    normalized = relative.replace("\\", "/")
    parts = PurePosixPath(normalized).parts
    if (PureWindowsPath(normalized).drive or normalized.startswith("/")
            or ".." in parts or ":" in normalized):
        raise RegistryError("Path must stay within workspace")
    if source and DENIED.search(normalized):
        raise RegistryError("Source is outside the non-PII pilot policy")
    path = (root / normalized).resolve()
    if not path.is_relative_to(root.resolve()):
        raise RegistryError("Symlink/junction escapes workspace")
    return path


def inspect_file(root, relative, kind="Document", expected_sha256=None):
    path = safe_path(root, relative, source=True)
    if not path.is_file():
        raise RegistryError("Missing source file")
    suffix = path.suffix.lower()
    with path.open("rb") as stream:
        head = stream.read(512)
    pictures = {".png": ("image/png", head.startswith(b"\x89PNG\r\n\x1a\n")),
                ".jpg": ("image/jpeg", head.startswith(b"\xff\xd8\xff")),
                ".jpeg": ("image/jpeg", head.startswith(b"\xff\xd8\xff")),
                ".webp": ("image/webp", head[:4] == b"RIFF" and head[8:12] == b"WEBP")}
    media = {".wav": ("audio/wav", head[:4] == b"RIFF" and head[8:12] == b"WAVE"),
             ".mp4": ("video/mp4", head[4:8] == b"ftyp"),
             ".mp3": ("audio/mpeg", head[:3] == b"ID3" or head[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"))}
    documents = {".json": ("application/json", head.lstrip(b"\xef\xbb\xbf \t\r\n")[:1] in (b"{", b"[")),
                 ".pdf": ("application/pdf", head.startswith(b"%PDF-")),
                 ".xlsx": ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", head.startswith(b"PK\x03\x04")),
                 ".xls": ("application/vnd.ms-excel", head.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1")),
                 ".md": ("text/markdown", b"\x00" not in head),
                 ".csv": ("text/csv", b"\x00" not in head),
                 ".txt": ("text/plain", b"\x00" not in head)}
    mime, valid = {"Document": documents, "Picture": pictures, "Media": media}.get(kind, {}).get(suffix, (None, False))
    if not valid:
        raise RegistryError("Unsupported format or signature/type mismatch")
    # Signature detection is not a full parser/security scan; adapters validate contents.
    before = path.stat()
    digest = sha256_file(path)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise RegistryError("Source changed during inspection")
    if expected_sha256 is not None and digest != expected_sha256:
        raise RegistryError("Source hash mismatch")
    return {"path": str(PurePosixPath(relative.replace("\\", "/"))), "sha256": digest,
            "size_bytes": after.st_size, "detected_mime": mime}


def validate_locator(locator, mime):
    if not isinstance(locator, dict):
        raise RegistryError("Locator must be an object")
    kind = locator.get("kind")
    allowed = {"file": set(), "json": {"pointer"},
               "spreadsheet": {"sheet_name", "row_number", "cell_ref", "value_mode"},
               "pdf": {"page_number", "object_ref"},
               "media_time": {"time_start_ms", "time_end_ms", "track"},
               "text": {"line_start", "line_end", "encoding"},
               "embedded_file": {"member_path"}}
    if kind not in allowed or set(locator) - allowed[kind] - {"kind"}:
        raise RegistryError("Unsupported locator fields; hold for adapter review")
    def positive(key):
        value = locator.get(key)
        return type(value) is int and value > 0
    valid = True
    if kind == "json":
        pointer = locator.get("pointer")
        valid = (mime == "application/json" and isinstance(pointer, str)
                 and (pointer == "" or pointer.startswith("/")) and not re.search(r"~(?![01])", pointer))
    elif kind == "spreadsheet":
        valid = ("spreadsheet" in mime or mime == "application/vnd.ms-excel") and positive("row_number")
        valid = valid and isinstance(locator.get("sheet_name"), str) and bool(locator["sheet_name"])
        valid = valid and bool(re.fullmatch(r"[A-Z]+[1-9][0-9]*", locator.get("cell_ref", "")))
        valid = valid and locator.get("value_mode") in ("formula", "cached_value", "literal", "unknown")
        if valid:
            valid = int(re.search(r"[0-9]+$", locator["cell_ref"])[0]) == locator["row_number"]
    elif kind == "pdf":
        valid = mime == "application/pdf" and positive("page_number")
    elif kind == "media_time":
        start, end = locator.get("time_start_ms"), locator.get("time_end_ms")
        valid = (mime.startswith(("audio/", "video/")) and type(start) is int and type(end) is int and 0 <= start <= end)
    elif kind == "text":
        valid = mime.startswith("text/") and positive("line_start") and positive("line_end")
        valid = valid and locator["line_start"] <= locator["line_end"] and locator.get("encoding") == "utf-8"
    elif kind == "embedded_file":
        safe_path(Path.cwd(), locator.get("member_path"))
    if not valid:
        raise RegistryError("Invalid locator or parent MIME")
    return deepcopy(locator)


class Registry:
    def __init__(self, workspace_root):
        self.root = Path(workspace_root).resolve()
        self.store = safe_path(self.root, STORE)
        schema = yaml.safe_load(SCHEMA.read_text(encoding="utf-8"))
        self.contract = {k: schema[k] for k in ("registry_contract", "registry_node_ontology", "registry_edge_ontology")}
        self.contract_hash = hashlib.sha256(canonical(self.contract).encode()).hexdigest()
        self.nodes, self.edges, self.identities = {}, {}, {}
        self.generation_id = None
        self.inputs = {}
        self._out, self._in = defaultdict(list), defaultdict(list)
        current = self._current()
        if current:
            self._load(current)
        self._baseline = self._digest()

    def _current(self):
        pointer = self.store / "CURRENT"
        if not pointer.exists():
            return None
        return self._generation_name(pointer.read_text(encoding="utf-8").strip())

    @staticmethod
    def _generation_name(value):
        if not isinstance(value, str) or not re.fullmatch(r"gen-[0-9a-f-]{36}", value):
            raise RegistryError("Invalid generation pointer")
        return value

    def _digest(self):
        return hashlib.sha256(canonical([self.nodes, self.edges, self.identities]).encode()).hexdigest()

    def _node(self, node_id, expected=None):
        node = self.nodes.get(node_id)
        if node is None or (node.get("tenant_id"), node.get("business_id")) != SCOPE:
            raise RegistryError("Missing or cross-scope node")
        if node.get("classification") != "product_metadata" or node.get("access_scope_ref") != ACCESS:
            raise RegistryError("Disallowed node access scope")
        if expected and node["type"] not in expected:
            raise RegistryError("Wrong endpoint type")
        return node

    def _new(self, kind, key, props):
        identity = canonical([kind, key])
        if identity in self.identities:
            existing = self._node(self.identities[identity], {kind})
            if existing["props"] != props:
                raise RegistryError("Identity collision or immutable metadata conflict")
            return existing["id"]
        node_id = self.contract["registry_node_ontology"][kind]["prefix"] + uuid7()
        stamp = now()
        self.nodes[node_id] = {"id": node_id, "type": kind, "tenant_id": SCOPE[0], "business_id": SCOPE[1],
                               "classification": "product_metadata", "access_scope_ref": ACCESS,
                               "registry_contract_version": self.contract["registry_contract"]["version"],
                               "registered_at": stamp, "updated_at": stamp, "lifecycle_status": "active", "props": props}
        self.identities[identity] = node_id
        return node_id

    def register_asset(self, relative_path, kind="Document", origin_key=None, expected_sha256=None,
                       classification="product_metadata", visual_origin="unknown"):
        if classification != "product_metadata" or visual_origin not in ("unknown", "source_photo", "crop", "render", "generated"):
            raise RegistryError("Source classification/visual origin requires review")
        info = inspect_file(self.root, relative_path, kind, expected_sha256)
        origin = origin_key or "local:" + info["path"]
        if not isinstance(origin, str) or not origin or DENIED.search(origin):
            raise RegistryError("Invalid origin key")
        asset = self._new(kind, origin, {"origin_key": origin, "visual_origin": visual_origin,
                                       "usage_rights": "unknown", "identity_status": "unresolved"})
        version_key = canonical(["AssetVersion", [asset, info["sha256"]]])
        if version_key in self.identities:
            version = self.identities[version_key]
            self._node(version, {"AssetVersion"})
        else:
            ordinal = 1 + len(self._out[asset])
            version = self._new("AssetVersion", [asset, info["sha256"]], {
                "owner_asset_id": asset, "sha256": info["sha256"], "size_bytes": info["size_bytes"],
                "detected_mime": info["detected_mime"], "ordinal": ordinal})
        location = self._new("FileLocation", info["path"], {"path": info["path"], "storage_scope": "workspace"})
        self.link("HAS_VERSION", asset, version)
        self.link("STORED_AT", version, location)
        self.inputs[info["path"]] = info["sha256"]
        return asset, version

    def link(self, rel, source, target):
        contract = self.contract["registry_edge_ontology"].get(rel)
        if contract is None:
            raise RegistryError("Unknown relationship")
        a, b = self._node(source, contract["from"]), self._node(target, contract["to"])
        if rel == "HAS_VERSION" and b["props"]["owner_asset_id"] != source:
            raise RegistryError("Version owner mismatch")
        if rel in ("HAS_ATTACHMENT", "ATTACHES_VERSION"):
            owner = b if rel == "HAS_ATTACHMENT" else a
            key = "owner_version_id" if rel == "HAS_ATTACHMENT" else "target_version_id"
            if owner["props"][key] != (source if rel == "HAS_ATTACHMENT" else target):
                raise RegistryError("Attachment endpoint mismatch")
        if rel == "ILLUSTRATES":
            raise RegistryError("Verified illustration adapter not enabled; retain unresolved evidence")
        edge_id = "edge:" + hashlib.sha256(canonical([SCOPE, rel, source, target]).encode()).hexdigest()
        if edge_id in self.edges:
            return edge_id
        if contract.get("acyclic"):
            queue, seen = [target], set()
            while queue:
                cursor = queue.pop()
                if cursor == source:
                    raise RegistryError("Derivation/dependency cycle")
                if cursor not in seen:
                    seen.add(cursor)
                    queue.extend(e["to"] for e in self._out[cursor] if e["rel"] == rel)
        edge = {"id": edge_id, "rel": rel, "from": source, "to": target,
                "tenant_id": SCOPE[0], "business_id": SCOPE[1]}
        self.edges[edge_id] = edge
        self._out[source].append(edge)
        self._in[target].append(edge)
        return edge_id

    def evidence(self, source_version_id, locator, record_kind="source_record", locator_status="file_only"):
        parent = self._node(source_version_id, {"AssetVersion"})
        locator = validate_locator(locator, parent["props"]["detected_mime"])
        if locator_status not in ("file_only", "prepared_record_only", "unknown"):
            raise RegistryError("Exact evidence requires a reconciled source adapter")
        if not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", record_kind):
            raise RegistryError("Invalid evidence kind")
        props = {"source_version_id": source_version_id, "source_sha256": parent["props"]["sha256"],
                 "locator": locator, "record_kind": record_kind, "locator_status": locator_status}
        result = self._new("EvidenceRecord", props, props)
        self.link("EXTRACTED_FROM", result, source_version_id)
        return result

    def attach(self, owner_version_id, target_version_id, locator, role="attachment"):
        owner = self._node(owner_version_id, {"AssetVersion"})
        self._node(target_version_id, {"AssetVersion"})
        locator = validate_locator(locator, owner["props"]["detected_mime"])
        if not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", role):
            raise RegistryError("Invalid attachment role")
        props = {"owner_version_id": owner_version_id, "target_version_id": target_version_id,
                 "locator": locator, "role": role}
        result = self._new("Attachment", props, props)
        self.link("HAS_ATTACHMENT", owner_version_id, result)
        self.link("ATTACHES_VERSION", result, target_version_id)
        return result

    def lookup_asset(self, node_id, scope=SCOPE):
        self._check_scope(scope)
        return deepcopy(self._node(node_id))

    @staticmethod
    def _check_scope(scope):
        if tuple(scope) != SCOPE:
            raise RegistryError("Scope denied")

    def _walk(self, node_id, direction, depth=4, max_nodes=500, max_edges=1000, time_budget_ms=1000, scope=SCOPE):
        self._check_scope(scope)
        for value, maximum in ((depth, 6), (max_nodes, 500), (max_edges, 1000), (time_budget_ms, 1000)):
            if type(value) is not int or not 1 <= value <= maximum:
                raise RegistryError("Traversal bound exceeded")
        self._node(node_id)
        deadline = time.monotonic() + time_budget_ms / 1000
        seen, edge_ids, queue = {node_id: 0}, set(), deque([(node_id, 0)])
        reason = None
        forward = {"HAS_VERSION", "STORED_AT", "DERIVED_FROM", "EXTRACTED_FROM", "DEPENDS_ON", "GENERATED_BY", "USED_INPUT"}
        backward = {"HAS_VERSION", "ATTACHES_VERSION", "HAS_ATTACHMENT"}
        if direction == "usages":
            forward, backward = backward, forward
        while queue:
            seed, level = queue.popleft()
            candidates = ((edge, edge["to"]) for edge in self._out[seed] if edge["rel"] in forward)
            reverse = ((edge, edge["from"]) for edge in self._in[seed] if edge["rel"] in backward)
            for edge, neighbor in itertools.chain(candidates, reverse):
                if time.monotonic() > deadline:
                    reason = "time_limit"
                    break
                if (edge["tenant_id"], edge["business_id"]) != SCOPE:
                    raise RegistryError("Cross-scope edge")
                self._node(neighbor)
                if neighbor in seen:
                    continue
                if level >= depth:
                    reason = reason or "depth_limit"
                    continue
                if len(seen) >= max_nodes:
                    reason = "node_limit"
                    break
                if len(edge_ids) >= max_edges:
                    reason = "edge_limit"
                    break
                seen[neighbor] = level + 1
                edge_ids.add(edge["id"])
                queue.append((neighbor, level + 1))
            if reason in ("time_limit", "node_limit", "edge_limit"):
                break
        return {"generation_id": self.generation_id, "node_ids": list(seen), "edge_ids": sorted(edge_ids),
                "truncated": reason is not None, "reason": reason}

    def trace_origin(self, node_id, **kwargs):
        return self._walk(node_id, "origin", **kwargs)

    def find_usages(self, node_id, **kwargs):
        return self._walk(node_id, "usages", **kwargs)

    def list_attachments(self, owner_version_id, limit=100, cursor=None, scope=SCOPE):
        self._check_scope(scope)
        self._node(owner_version_id, {"AssetVersion"})
        if type(limit) is not int or not 1 <= limit <= 100:
            raise RegistryError("Page size exceeded")
        binding = hashlib.sha256(canonical([owner_version_id, self.generation_id, self._digest()]).encode()).hexdigest()
        offset = 0
        if cursor is not None:
            if not isinstance(cursor, str) or not re.fullmatch(r"[0-9a-f]{64}:[0-9]+", cursor):
                raise RegistryError("Malformed cursor")
            token, offset = cursor.split(":")
            if token != binding:
                raise RegistryError("Stale or wrong-owner cursor")
            offset = int(offset)
        ids = [edge["to"] for edge in self._out[owner_version_id] if edge["rel"] == "HAS_ATTACHMENT"]
        if offset > len(ids):
            raise RegistryError("Cursor out of bounds")
        items = [deepcopy(self._node(i, {"Attachment"})) for i in ids[offset:offset+limit]]
        end = offset + len(items)
        return {"items": items, "next_cursor": f"{binding}:{end}" if end < len(ids) else None}

    def validate(self):
        ontology = self.contract["registry_node_ontology"]
        version_keys, ordinals = set(), set()
        for node_id, node in self.nodes.items():
            self._node(node_id)
            common = self.contract['registry_contract']['common_required']
            if (set(node) != set(common) or node.get('registry_contract_version') != self.contract['registry_contract']['version']
                    or node.get('lifecycle_status') != 'active'):
                raise RegistryError('Common metadata contract mismatch')
            kind, props = node.get("type"), node.get("props")
            if kind not in ontology or not isinstance(props, dict) or node.get("id") != node_id:
                raise RegistryError("Invalid node shape")
            prefix = ontology[kind]["prefix"]
            try:
                valid_id = node_id.startswith(prefix) and UUID(node_id[len(prefix):]).version == 7
            except ValueError:
                valid_id = False
            if not valid_id or set(props) != set(ontology[kind]["required_properties"]):
                raise RegistryError("ID/property contract mismatch")
            if kind == "AssetVersion":
                self._node(props["owner_asset_id"], {"Document", "Picture", "Media"})
                key = (props["owner_asset_id"], props["sha256"])
                ordinal = (props["owner_asset_id"], props["ordinal"])
                if (not re.fullmatch(r"[0-9a-f]{64}", props["sha256"]) or key in version_keys
                        or ordinal in ordinals or type(props["ordinal"]) is not int or props["ordinal"] < 1
                        or type(props["size_bytes"]) is not int or props["size_bytes"] < 0):
                    raise RegistryError("Invalid or duplicate version")
                version_keys.add(key)
                ordinals.add(ordinal)
            elif kind == "FileLocation":
                safe_path(self.root, props["path"], source=True)
            elif kind in ("Attachment", "EvidenceRecord"):
                parent_key = "owner_version_id" if kind == "Attachment" else "source_version_id"
                parent = self._node(props[parent_key], {"AssetVersion"})
                validate_locator(props["locator"], parent["props"]["detected_mime"])
                if kind == "EvidenceRecord" and props["source_sha256"] != parent["props"]["sha256"]:
                    raise RegistryError("Evidence hash is not pinned to parent")
        edges = list(self.edges.values())
        self.edges, self._out, self._in = {}, defaultdict(list), defaultdict(list)
        for edge in edges:
            if (edge.get("tenant_id"), edge.get("business_id")) != SCOPE:
                raise RegistryError("Cross-scope edge")
            new_id = self.link(edge["rel"], edge["from"], edge["to"])
            if new_id != edge["id"]:
                raise RegistryError("Edge identity mismatch")
        for target in self.identities.values():
            self._node(target)
        for node_id, node in self.nodes.items():
            props = node['props']
            outgoing = {(e['rel'], e['to']) for e in self._out[node_id]}
            incoming = {(e['rel'], e['from']) for e in self._in[node_id]}
            if node['type'] == 'AssetVersion':
                if ('HAS_VERSION', props['owner_asset_id']) not in incoming or not any(r == 'STORED_AT' for r, _ in outgoing):
                    raise RegistryError('Version requires owner and location edges')
            elif node['type'] == 'Attachment':
                if (('HAS_ATTACHMENT', props['owner_version_id']) not in incoming
                        or ('ATTACHES_VERSION', props['target_version_id']) not in outgoing):
                    raise RegistryError('Incomplete attachment binding')
            elif node['type'] == 'EvidenceRecord':
                if ('EXTRACTED_FROM', props['source_version_id']) not in outgoing:
                    raise RegistryError('Evidence requires pinned source edge')
        return True

    def _load(self, generation):
        try:
            directory = safe_path(self.root, f"{STORE}/generations/{self._generation_name(generation)}")
            manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
            if (manifest["generator"] != GENERATOR or manifest["generation_id"] != generation
                    or manifest["contract_sha256"] != self.contract_hash or manifest["scope"] != list(SCOPE)):
                raise RegistryError("Generation ownership/contract mismatch")
            data = {}
            for name in ("nodes", "edges", "identity_map"):
                path = directory / f"{name}.jsonl"
                if sha256_file(path) != manifest["checksums"][path.name]:
                    raise RegistryError("Generation checksum mismatch")
                rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
                key = "key" if name == "identity_map" else "id"
                data[name] = {row[key]: row for row in rows}
                if len(data[name]) != len(rows) or len(rows) != manifest["counts"][name]:
                    raise RegistryError("Duplicate IDs or count mismatch")
            self.nodes, self.edges = data["nodes"], data["edges"]
            self.identities = {key: value["id"] for key, value in data["identity_map"].items()}
            self.validate()
            self.generation_id = generation
        except (KeyError, TypeError, OSError, json.JSONDecodeError) as exc:
            raise RegistryError("Malformed or unavailable generation") from exc

    @contextmanager
    def _writer(self):
        # Resolve again to reject a junction substituted after the reader opened.
        self.store = safe_path(self.root, STORE)
        self.store.mkdir(parents=True, exist_ok=True)
        lock = self.store / "WRITER.lock"
        try:
            descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError as exc:
            raise RegistryError("Writer lock exists; inspect owner before manual recovery") from exc
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                stream.write(canonical({"pid": os.getpid(), "created_at": now(), "generator": GENERATOR}))
                stream.flush()
                os.fsync(stream.fileno())
            if self._current() != self.generation_id:
                raise RegistryError("Stale writer; reload current generation")
            yield
        finally:
            lock.unlink()

    def _publish_pointer(self, generation):
        with tempfile.NamedTemporaryFile(dir=self.store, prefix=".CURRENT-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write((generation + "\n").encode())
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.replace(temporary, self.store / "CURRENT")
        finally:
            temporary.unlink(missing_ok=True)

    def _check_inputs(self):
        for path, digest in self.inputs.items():
            if sha256_file(safe_path(self.root, path, source=True)) != digest:
                raise RegistryError('Input changed before publish; candidate remains inactive')

    def _audit_intent(self, generation, operation):
        path = safe_path(self.root, f'{STORE}/audit/events.jsonl')
        path.parent.mkdir(parents=True, exist_ok=True)
        previous = None
        if path.exists():
            with path.open(encoding='utf-8') as stream:
                for line in stream:
                    entry = json.loads(line)
                    digest = entry.pop('sha256')
                    if (entry['previous_sha256'] != previous or
                            hashlib.sha256(canonical(entry).encode()).hexdigest() != digest):
                        raise RegistryError('Audit chain mismatch')
                    previous = digest
        entry = {'generator': GENERATOR, 'operation': operation, 'status': 'publish_intent',
                 'from_generation_id': self.generation_id, 'to_generation_id': generation,
                 'at': now(), 'previous_sha256': previous}
        entry['sha256'] = hashlib.sha256(canonical(entry).encode()).hexdigest()
        with path.open('a', encoding='utf-8', newline='\n') as stream:
            stream.write(canonical(entry) + '\n')
            stream.flush()
            os.fsync(stream.fileno())

    def commit(self):
        with self._writer():
            self.validate()
            self._check_inputs()
            if self.generation_id and self._digest() == self._baseline:
                return self.generation_id
            generation = "gen-" + uuid7()
            directory = safe_path(self.root, f"{STORE}/generations/{generation}")
            directory.mkdir(parents=True, exist_ok=False)
            records = {"nodes": self.nodes.values(), "edges": self.edges.values(),
                       "identity_map": [{"key": key, "id": value} for key, value in sorted(self.identities.items())]}
            checksums, counts = {}, {}
            for name, values in records.items():
                values = list(values)
                path = directory / f"{name}.jsonl"
                with path.open("x", encoding="utf-8", newline="\n") as stream:
                    for value in values:
                        stream.write(canonical(value) + "\n")
                    stream.flush()
                    os.fsync(stream.fileno())
                checksums[path.name], counts[name] = sha256_file(path), len(values)
            manifest = {"generator": GENERATOR, "generation_id": generation, "parent_generation_id": self.generation_id,
                        "scope": list(SCOPE), "contract_sha256": self.contract_hash, "created_at": now(),
                        "checksums": checksums, "counts": counts, "inputs": self.inputs}
            with (directory / "manifest.json").open("x", encoding="utf-8") as stream:
                stream.write(canonical(manifest) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
            # Re-read candidate before activation; don't make it current on a partial write.
            verifier = Registry(self.root)
            verifier._load(generation)
            self._audit_intent(generation, 'commit')
            self._check_inputs()
            self._publish_pointer(generation)
            self.generation_id, self._baseline = generation, self._digest()
            return generation

    def rollback(self, generation):
        with self._writer():
            verifier = Registry(self.root)
            cursor, ancestors = self.generation_id, set()
            while cursor is not None:
                if cursor in ancestors or len(ancestors) >= 1000:
                    raise RegistryError('Invalid or excessive generation ancestry')
                ancestors.add(cursor)
                verifier._load(cursor)
                manifest_path = safe_path(self.root, f'{STORE}/generations/{cursor}/manifest.json')
                cursor = json.loads(manifest_path.read_text(encoding='utf-8'))['parent_generation_id']
            if generation not in ancestors:
                raise RegistryError('Rollback target must be a committed ancestor, not an inactive candidate')
            verifier._load(generation)
            self._audit_intent(generation, 'rollback')
            self._publish_pointer(generation)
            self._load(generation)
            self.inputs = {}
            self._baseline = self._digest()
