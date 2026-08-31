---
version: "0.3.0b"
created_at: "2026-08-09T18:20:00+07:00, ATHER, uncommitted"
last_update: "2026-08-10T00:10:00+07:00, ATHER"
status: "draft"
superseded_by: null
attributes:
  domain: "visual-ai-marketing"
  scope: "runtime-and-contract-specification"
  artifact_id: "SPEC-VAMT-001"
---

# SPEC — Visual AI Agent Marketing Team

## SPEC-0. Status และ Normative Language

เอกสารนี้เป็น contract draft สำหรับ implementation หลัง approval ของ PRD-VAMT-001 และ SRS-VAMT-001 เท่านั้น

- MUST/SHALL: บังคับ
- MUST NOT/SHALL NOT: ข้อห้าม
- SHOULD: ต้องปฏิบัติเว้นแต่มี decision ที่อ้างอิงได้
- MAY: ทำได้แต่ไม่ใช่ acceptance requirement

## SPEC-1. Canonical Identifiers

| Object | Pattern | ตัวอย่าง |
|---|---|---|
| Tenant | tenant:{slug} | tenant:smartgift |
| Campaign | cmp_{ulid} | cmp_01J... |
| Flow run | run_{ulid} | run_01J... |
| Task | task_{ulid} | task_01J... |
| GKS atom | gks:{type}:{slug}:{semver} | gks:brand_palette:smartgift:1.0.0 |
| Candidate atom | candidate:{type}:{ulid} | candidate:research_fact:01J... |
| Human decision | msp:{ulid} | msp:01J... |
| Asset | asset:{ulid} | asset:01J... |
| Artifact | artifact:{sha256} | artifact:sha256:... |
| Package | package:{ulid} | package:01J... |
| Event | evt_{ulid} | evt_01J... |
| Checkpoint | cp_{ulid} | cp_01J... |
| Incident | inc_{ulid} | inc_01J... |

Identifier ห้าม encode PII, raw customer name, phone, provider secret หรือ commercial claim ที่ยังไม่อนุมัติ

## SPEC-2. Repository and Runtime Layout

~~~text
knowledge/
  atoms/                 canonical and approved atomic knowledge
  candidates/            unpromoted observations only
  manifests/             immutable knowledge snapshots
agents/
  {role}/
    system-prompt.md
    capability-manifest.yaml
    output-schema.json
workflows/
  campaign-lifecycle/
  b2b/
  c2c/
  recovery/
schemas/
policies/
  brand/
  model-routing/
  rights-and-licensing/
  human-gates/
  pdpa-and-retention/
state/
  migrations/
  replay/
  fixtures/
campaigns/
  {campaign_id}/
    brief/
    concept/
    approvals/
    manifests/
    reports/
integrations/
  govibe/
  msp/
  gks/
  genesisblockdb/
  fung/
  image-providers/
  analytics/
  publishing/
observability/
tests/
~~~

Production durable state, object bytes, secure transcripts and secrets MUST NOT live in the source repository. The directories above contain contracts, manifests, fixtures and non-sensitive references only.

### 2.1 Authority contract (SPEC-AUTHORITY)

| System | Normative authority | Required persisted evidence | Prohibited authority |
|---|---|---|---|
| GoVibe | approved execution configuration, workflow topology, capability/model routing constraints | `config_snapshot_ref`, `config_hash`, `config_version` | human decision, canonical business truth |
| MSP | signed gate decision, quorum aggregation, exception, revocation and GKS promotion authorization | decision/quorum/exception refs and hashes | direct canonical storage mutation |
| GKS | candidate/canonical atom registry, validity, supersession and authorized read/mutation contract | atom ID/version/content hash/status/validity | workflow control state |
| GenesisBlockDB | tenant-aware materialization and index of GKS relations | source GKS ref/hash and projection timestamp | promotion, canonical mutation or decision authority |

Every event and checkpoint MUST reference the active GoVibe config snapshot. Replay MUST resolve the same snapshot; unavailable or hash-mismatched configuration enters MANUAL_REVIEW. A GenesisBlockDB projection MUST be rejected when its source GKS ref/hash/status differs from GKS and MUST NOT repair or promote the source record.

## SPEC-3. Role Contracts (SPEC-ROLE)

| Role ID | Reads | May write | Must not do |
|---|---|---|---|
| orchestrator | brief, policy, state, approved decisions | task state, event, checkpoint, gate request | create creative, approve, publish |
| brand_visual_guardian | brand/product/channel atoms, concept/spec/candidate | brand finding/decision proposal | change brand atom, generate, authorize exception |
| visual_research | approved brief and source allowlist | research packet, candidate atoms | state claim as fact without provenance |
| creative_concept_director | research, approved atoms, brief | concept deck, asset spec draft | generate or select final route |
| visual_asset_generator | locked asset spec, model binding, G3 decision | asset candidate, provider/job evidence | modify scope, add claim, overwrite asset |
| copy_visual_integrator | approved copy/claim atoms, candidate asset | composition, accessibility metadata | create claim/price or publish |
| performance_optimization | verified SoT snapshots and experiment policy | finding, experiment proposal | mutate media/budget/channel directly |
| campaign_packager | approved assets, decisions, rights | package manifest/release request | alter creative or release |
| fung_adapter | consented media/meeting context | redacted evidence package | treat speech as human approval |

### Required Agent Output Envelope

~~~json
{
  "schema_version": "1.0",
  "status": "COMPLETED",
  "tenant_id": "tenant:example",
  "campaign_id": "cmp_01J...",
  "run_id": "run_01J...",
  "task_id": "task_01J...",
  "config_snapshot_ref": "artifact:sha256:...",
  "config_hash": "sha256:...",
  "config_version": "govibe-config-1.0.0",
  "role_id": "visual_research",
  "input_snapshot_hash": "sha256:...",
  "output_ref": "artifact:sha256:...",
  "state_patch": [],
  "evidence_refs": ["gks:..."],
  "missing_requirements": [],
  "audit_event_refs": ["evt_01J..."]
}
~~~

Allowed status values are COMPLETED, BLOCKED, WAITING_EXTERNAL, NEEDS_REVIEW and FAILED. An agent MUST NOT return APPROVED; approval is an MSP human-decision value only.

## SPEC-4. Campaign Brief Contract (SPEC-BRIEF)

### Required fields

~~~json
{
  "schema_version": "1.0",
  "campaign_id": "cmp_01J...",
  "tenant_id": "tenant:smartgift",
  "market_motion": "B2B",
  "objective": {
    "type": "lead_generation",
    "metric_definition_ref": "gks:campaign_metric:qualified_lead:1.0.0"
  },
  "audience_refs": ["gks:audience_persona:..."],
  "product_truth_refs": ["gks:product_truth:..."],
  "brand_profile_ref": "gks:brand_identity:...:1.0.0",
  "channel_plan": [
    {
      "channel_ref": "gks:channel_spec:linkedin:1.0.0",
      "locale": "th-TH",
      "format_refs": ["gks:visual_format:linkedin-single-image:1.0.0"]
    }
  ],
  "constraints": {
    "deadline": "2026-09-01T09:00:00+07:00",
    "budget_ceiling": 0,
    "rights_policy_ref": "gks:rights_policy:...:1.0.0",
    "prohibited_claim_refs": ["gks:prohibited_claim:..."]
  },
  "provenance": {
    "submitted_by": "principal:marketing_owner",
    "submitted_at": "2026-08-09T18:00:00+07:00",
    "source_refs": ["evidence:brief-submission:..."]
  }
}
~~~

Validation order MUST be:

1. syntactic schema and identifier validation
2. caller tenant/role authorization
3. atom resolve, status, validity and relation checks
4. product/claim/channel/rights policy compatibility
5. campaign uniqueness and idempotency
6. event creation and initial checkpoint

## SPEC-5. Campaign State Contract (SPEC-STATE)

### 5.1 State partition

| Partition | Authoritative owner | State content |
|---|---|---|
| control | PersistentFlow/event ledger | phase, node, task, retry, gate, checkpoint |
| knowledge | GKS/GenesisBlockDB | atom version refs and snapshot hash |
| artifact | object store/artifact registry | URI, checksum, lineage, technical status |
| decision | MSP | signature, authority, scope, expiry |
| metric | analytics SoT | source-stamped snapshot only |
| sensitive | FUNG secure vault | raw audio/transcript/PII mapping |

### 5.2 Persisted state

~~~json
{
  "schema_version": "1.0",
  "campaign_id": "cmp_01J...",
  "run_id": "run_01J...",
  "revision": 42,
  "status": "WAITING_FOR_HUMAN",
  "current_node": "gate_g4_final_visual",
  "knowledge_snapshot": {
    "manifest_ref": "artifact:sha256:...",
    "content_hash": "sha256:..."
  },
  "workflow": {
    "completed_nodes": ["validate_brief", "research"],
    "in_flight": [],
    "idempotency_index_ref": "artifact:sha256:..."
  },
  "artifacts": {
    "asset_refs": ["asset:01J..."],
    "package_ref": null,
    "quarantine_refs": []
  },
  "gates": {
    "pending": {
      "gate_id": "G4",
      "subject_hash": "sha256:...",
      "required_roles": ["brand_owner"],
      "expires_at": "2026-08-12T18:00:00+07:00"
    },
    "decision_refs": ["msp:01J..."]
  },
  "audit": {
    "event_head_hash": "sha256:...",
    "last_checkpoint_ref": "cp_01J..."
  },
  "recovery": {
    "mode": "NONE",
    "last_consistent_revision": 42
  }
}
~~~

### 5.3 Allowed lifecycle states

| State | Permitted next state |
|---|---|
| INTAKE | PLANNING, WAITING_FOR_HUMAN, BLOCKED |
| PLANNING | WAITING_FOR_HUMAN, GENERATING, BLOCKED |
| WAITING_FOR_HUMAN | INTAKE, PLANNING, GENERATING, PACKAGING, READY_FOR_RELEASE, LIVE, OPTIMIZING, BLOCKED |
| GENERATING | REVIEWING, RECOVERING, BLOCKED |
| REVIEWING | WAITING_FOR_HUMAN, PLANNING, BLOCKED |
| PACKAGING | READY_FOR_RELEASE, BLOCKED |
| READY_FOR_RELEASE | WAITING_FOR_HUMAN, BLOCKED |
| LIVE | WAITING_FOR_HUMAN, OPTIMIZING, CLOSED, RECOVERING |
| OPTIMIZING | GENERATING, CLOSED, WAITING_FOR_HUMAN |
| RECOVERING | prior safe state, MANUAL_REVIEW |
| MANUAL_REVIEW | PLANNING, BLOCKED |
| BLOCKED | PLANNING, CLOSED |
| CLOSED | none |

An unlisted transition MUST fail validation before any state write.

## SPEC-6. Event and Checkpoint Contract (SPEC-EVENT)

### 6.1 Event envelope

~~~json
{
  "event_id": "evt_01J...",
  "event_type": "GENERATION_REQUESTED",
  "occurred_at": "2026-08-09T18:00:00+07:00",
  "tenant_id": "tenant:smartgift",
  "campaign_id": "cmp_01J...",
  "run_id": "run_01J...",
  "task_id": "task_01J...",
  "actor": {
    "kind": "agent",
    "id": "visual_asset_generator"
  },
  "idempotency_key": "sha256:...",
  "input_hash": "sha256:...",
  "payload_ref": "artifact:sha256:...",
  "previous_event_hash": "sha256:...",
  "event_hash": "sha256:..."
}
~~~

Event payload MUST contain references or redacted data only. Never put secret, raw transcript, raw prompt containing PII, binary asset or access token in event payload.

### 6.2 Transactional outbox and checkpoint policy

Idempotency uniqueness scope is `(tenant_id, adapter_id, operation_class, idempotency_key)`. The key MUST derive from canonical input hash and intended side-effect scope. Reuse of the scoped key with a different canonical input hash is `IDEMPOTENCY_CONFLICT`, enters MANUAL_REVIEW and MUST NOT dispatch.

The durable order is normative:

1. Build the canonical outgoing payload and verify request-path PII evidence.
2. In one database transaction, compare-and-swap the expected state revision, reserve the idempotency scope, append `NODE_INTENT`, create `OUTBOX_PENDING`, update event head and commit a checkpoint containing the GoVibe config snapshot. No adapter call is allowed before this commit succeeds.
3. A dispatcher claims the committed outbox row with a lease and sends the exact canonical payload hash. A retry sends the same scoped idempotency key and payload only.
4. On provider acceptance, persist `provider_job_id`, provider acknowledgement and `OUTBOX_ACCEPTED` with state-revision CAS before acknowledging the worker message.
5. A terminal response or webhook is deduplicated by `(tenant_id, adapter_id, provider_event_id)` or, when unavailable, `(provider_job_id, terminal_result_hash)`. Persist the receipt/result as `RESULT_PENDING_ADMISSION`; do not mutate authoritative artifact/campaign state yet.
6. Apply SPEC-6.4 admission. Only `RESULT_ADMITTED` may update authoritative state. Commit result event, state CAS and checkpoint atomically, then mark the outbox terminal.

| Trigger | Minimum checkpoint content |
|---|---|
| outbox commit before dispatch | intent event, scoped idempotency reservation, canonical input hash, PII scan ref, expected/new revision, config snapshot ref/hash/version |
| after provider accepts job | provider job ID, acknowledgement hash, provider binding, pending status |
| after terminal tool result | dedupe key, output refs/hash, admission status, error class if any |
| before gate | exact review subject hash, required quorum policy/version, policy version |
| after decision | per-signer refs, aggregate decision hash/status, next node |
| before release | package manifest hash, PII scan ref and release scope |
| after release | external receipt/reconciliation state |
| recovery start/end | reason, reconciled operation list, consistent revision and config snapshot |

### 6.3 Recovery truth table

Recovery first loads the latest checkpoint whose state hash, event head and GoVibe config snapshot validate, then reconciles every non-terminal outbox row. Missing schema migration or configuration enters MANUAL_REVIEW.

| Adapter observation | Required action | Replacement dispatch allowed |
|---|---|---|
| ACCEPTED with terminal result | persist once as RESULT_PENDING_ADMISSION, dedupe, then run SPEC-6.4 | No |
| ACCEPTED/PENDING | persist latest acknowledgement and wait/poll the same provider job | No |
| NOT_FOUND with proof that provider never accepted the scoped key | append reconciliation evidence; reset the same outbox row to PENDING and dispatch the same key/payload | Yes, same operation only |
| NOT_FOUND without non-acceptance proof | enter MANUAL_REVIEW as AMBIGUOUS | No |
| AMBIGUOUS, timeout without query support, conflicting receipt or idempotency hash conflict | enter MANUAL_REVIEW and block downstream side effects | No |

Recovery MUST append events and checkpoints; it MUST NOT delete evidence, create a new idempotency key for the same intended operation or infer non-acceptance from absence alone.

### 6.4 External-result admission

Before authoritative ingest, the evaluator MUST verify: tenant/run/operation identity; result and original canonical payload hashes; exact reviewed subject hash; active aggregate gate decision and quorum; current policy/model/provider binding; and every referenced GKS atom status, validity, content hash and supersession relation. Admission uses the original GoVibe config snapshot plus current revocation/supersession facts.

If any approval is expired/revoked, a subject or payload hash differs, a policy no longer permits admission, or an atom is invalid/superseded in a way that invalidates scope, the result MUST become an immutable `STALE_RESULT` quarantine record with reason and superseding refs. It MUST NOT be merged into campaign/artifact authority, packaged, published or automatically replayed. A new explicit MSP decision may authorize a new operation; it cannot rewrite or silently admit the quarantined result.

## SPEC-7. Human Gate Contract (SPEC-GATE)

| Gate | Subject hash comprises | Required authority |
|---|---|---|
| G0 | brief + consent/data authority + knowledge snapshot | Marketing Owner or Sales Lead under policy |
| G1 | selected brand profile and brand applicability report | Brand Owner |
| G2 | concept route, message hierarchy and asset spec draft | Marketing Owner + Brand Owner where policy requires |
| G3 | locked asset spec, model/provider binding, cost/reservation, exception refs | Marketing Owner; Finance if threshold applies |
| G4 | selected visual candidates and Guardian finding | Brand Owner |
| G5 | copy, claim evidence, disclaimer, rights packet | Legal + Marketing Owner |
| G6 | immutable package manifest and intended destinations | Marketing Owner |
| G7 | experiment design, metric, guardrail and stop condition | Marketing Owner |

### Decision object

~~~json
{
  "decision_id": "msp:01J...",
  "gate_request_id": "gate-request:01J...",
  "gate_id": "G4",
  "campaign_id": "cmp_01J...",
  "subject_refs": ["asset:01J...#revision=2"],
  "subject_hash": "sha256:...",
  "decision": "APPROVE",
  "conditions": [],
  "actor": {
    "principal_id": "principal:brand_owner_1",
    "role": "brand_owner"
  },
  "authority": {
    "policy_ref": "gks:human_gate_policy:...:1.0.0",
    "quorum_policy_ref": "gks:gate_quorum_policy:...:1.0.0",
    "quorum_policy_version": "1.0.0",
    "scope_hash": "sha256:..."
  },
  "decided_at": "2026-08-09T18:00:00+07:00",
  "expires_at": "2026-08-23T18:00:00+07:00",
  "signature": "provider-specific-signature"
}
~~~

Resume MUST verify all fields above, including subject hash and expiry. A REQUEST_REVISION decision MUST create a new revision, not mutate the reviewed subject.

### 7.1 Multi-authority quorum

G2 and G5 gate requests MUST contain `quorum_policy_ref`, `quorum_policy_version`, exact required roles/principals, threshold rule and subject hash. Each signer creates an immutable decision with unique `(gate_request_id, principal_id, subject_hash, quorum_policy_version)`; an exact duplicate returns the prior decision, while a different decision under the same uniqueness scope is a conflict and requires explicit superseding/revocation evidence.

~~~json
{
  "gate_request_id": "gate-request:01J...",
  "gate_id": "G5",
  "campaign_id": "cmp_01J...",
  "subject_hash": "sha256:...",
  "quorum_policy_ref": "gks:gate_quorum_policy:...:1.0.0",
  "quorum_policy_version": "1.0.0",
  "required_roles": ["legal", "marketing_owner"],
  "threshold": {"kind": "ALL_REQUIRED_ROLES"},
  "expires_at": "2026-08-23T18:00:00+07:00"
}
~~~

The aggregate object MUST contain ordered signer decision refs, quorum policy ref/version, subject hash, aggregate status and `aggregate_hash`. Status calculation is deterministic: any active authorized REJECT produces REJECTED; otherwise any active revocation or required-signature expiry produces EXPIRED; otherwise a REQUEST_REVISION produces REVISION_REQUESTED; otherwise satisfying every required role/threshold produces APPROVED; otherwise PENDING. Concurrent signing MUST use CAS on the aggregate revision and recompute from immutable signer decisions. No partial or PENDING aggregate grants downstream authority.

~~~json
{
  "gate_request_id": "gate-request:01J...",
  "aggregate_revision": 3,
  "subject_hash": "sha256:...",
  "quorum_policy_ref": "gks:gate_quorum_policy:...:1.0.0",
  "quorum_policy_version": "1.0.0",
  "ordered_signer_decision_refs": ["msp:01J...", "msp:01K..."],
  "status": "APPROVED",
  "aggregate_hash": "sha256:..."
}
~~~

### 7.2 Canonical gate outcome-to-state mapping

The package/artifact remains immutable across every mapping. `REJECT` includes aggregate REJECTED; `EXPIRE` includes signature, quorum-policy or gate expiry.

| Gate | APPROVE | REJECT | EXPIRE | REQUEST_REVISION |
|---|---|---|---|---|
| G0 | PLANNING | BLOCKED | BLOCKED | INTAKE |
| G1 | PLANNING | PLANNING | PLANNING | PLANNING |
| G2 | PLANNING | PLANNING | PLANNING | PLANNING |
| G3 | GENERATING | PLANNING | PLANNING | PLANNING |
| G4 | PLANNING | PLANNING | PLANNING | PLANNING |
| G5 | PACKAGING | PLANNING | PLANNING | PLANNING |
| G6 | LIVE | READY_FOR_RELEASE | READY_FOR_RELEASE | PACKAGING |
| G7 | OPTIMIZING | LIVE | LIVE | LIVE |

Opening a gate transitions to WAITING_FOR_HUMAN and records `prior_safe_state`. Applying an outcome MUST validate the table target against SPEC-STATE. Where the target equals the prior state, the runtime still commits a new state revision and decision event. No outcome may select an implementation-defined fallback state.

## SPEC-8. Knowledge Atom Contract (SPEC-ATOM)

### Required atom envelope

~~~yaml
atom_id: gks:brand_visual_tone:smartgift:1.0.0
atom_type: brand_visual_tone
status: canonical
tenant_id: tenant:smartgift
version: 1.0.0
content_hash: sha256:...
provenance:
  source_refs:
    - artifact:sha256:...
  created_by: principal:brand_owner_1
  created_at: 2026-08-09T18:00:00+07:00
validity:
  effective_from: 2026-08-09T18:00:00+07:00
  effective_to: null
relations:
  - relation_type: constrains
    target_atom_id: gks:asset_spec:...
    provenance_ref: msp:01J...
access_classification: internal
supersedes: null
~~~

The minimum atom set before G0 is:

- brand identity, tone, palette, typography, logo and forbidden visual rules
- product truth and approved product imagery/rights
- approved claims, prohibited claims and disclaimers
- audience/persona and channel specification
- rights, model-route, generation-safety, human-gate and budget policies
- metric definition and experiment policy

Candidate atom promotion MUST be external to agent runtime and use MSP-authorized GKS mutation.

## SPEC-9. Asset and Generation Contract (SPEC-ASSET and SPEC-GENERATION)

### 9.1 Locked asset specification

~~~json
{
  "asset_spec_id": "gks:asset_spec:cmp_01J-primary:1.0.0",
  "status": "LOCKED",
  "campaign_id": "cmp_01J...",
  "brand_snapshot_hash": "sha256:...",
  "objective_ref": "gks:...",
  "subject_refs": ["gks:product_truth:..."],
  "composition": {
    "aspect_ratio": "1:1",
    "safe_area_ref": "gks:visual_format:...",
    "focal_hierarchy": ["product", "headline_space", "logo"]
  },
  "approved_prompt_fragment_refs": ["gks:prompt_fragment:..."],
  "forbidden_visual_refs": ["gks:forbidden_visual:..."],
  "required_disclaimer_refs": ["gks:legal_disclaimer:..."],
  "source_asset_refs": ["asset:approved-product-shot"],
  "generation_decision_ref": "msp:01J..."
}
~~~

### 9.2 Provider request contract

~~~json
{
  "request_id": "req_01J...",
  "idempotency_key": "sha256:...",
  "tenant_id": "tenant:smartgift",
  "campaign_id": "cmp_01J...",
  "asset_spec_ref": "gks:asset_spec:...",
  "model_binding_ref": "gks:model_binding:...",
  "prompt_record_ref": "secure:prompt:...",
  "prompt_hash": "sha256:...",
  "negative_prompt_hash": "sha256:...",
  "parameter_hash": "sha256:...",
  "source_asset_refs": ["asset:..."],
  "data_processing_approval_ref": "msp:01J...",
  "pii_scan_ref": "artifact:sha256:..."
}
~~~

Provider adapter MUST return provider_job_id if it has accepted the request. A provider that cannot retrieve status by job ID or idempotency key is not eligible for production G3 scope until a compensating reconciliation contract is approved.
Provider adapter MUST reject a request when data_processing_approval_ref is absent, expired, outside the data class/geography of the model binding, or does not cover the intended provider.

`pii_scan_ref` MUST resolve to immutable evidence with this minimum contract:

~~~json
{
  "scan_id": "scan:01J...",
  "canonical_outgoing_payload_hash": "sha256:...",
  "data_class": "internal",
  "scanner_id": "approved-scanner-id",
  "scanner_version": "1.0.0",
  "policy_ref": "gks:pii_policy:...:1.0.0",
  "policy_version": "1.0.0",
  "result": "PASS",
  "finding_count": 0,
  "approved_finding_refs": [],
  "scanned_at": "2026-08-09T18:00:00+07:00",
  "expires_at": "2026-08-09T19:00:00+07:00"
}
~~~

The canonical outgoing payload includes every field and source artifact actually sent to the provider after redaction/serialization. Before writing NODE_INTENT or GENERATION_REQUESTED, the runtime MUST resolve the evidence, recompute the payload hash and verify data class, active scanner/policy allowlist, `result=PASS`, zero unapproved findings and unexpired time. Any mismatch fails closed without creating an outbox row or external call.

### 9.3 Asset manifest

~~~json
{
  "asset_id": "asset:01J...",
  "revision": 1,
  "state": "CANDIDATE",
  "artifact": {
    "uri": "object://tenant-smartgift/campaign/cmp_01J/asset/...",
    "sha256": "sha256:...",
    "mime_type": "image/png",
    "width": 1080,
    "height": 1080
  },
  "lineage": {
    "parent_asset_refs": [],
    "asset_spec_ref": "gks:asset_spec:...",
    "prompt_hash": "sha256:...",
    "model_binding_ref": "gks:model_binding:...",
    "render_parameters_hash": "sha256:...",
    "seed": null
  },
  "rights": {
    "policy_ref": "gks:rights_policy:...",
    "source_refs": ["gks:approved_product_image:..."],
    "status": "VERIFIED"
  },
  "quality": {
    "technical_check_refs": ["artifact:sha256:..."],
    "brand_decision_ref": null
  },
  "audit_event_refs": ["evt_01J..."]
}
~~~

## SPEC-10. Multi-LLM Routing

### Model Binding

~~~yaml
binding_id: gks:model_binding:visual-generator-a:1.0.0
task_class: image_generation
provider: approved-provider-id
model: approved-model-id
model_version: provider-reported-version
data_class_max: confidential
region: approved-region
safety_policy_ref: gks:generation_safety_policy:...:1.0.0
data_processing_approval_ref: msp:01J...
cost_ceiling_ref: gks:budget_policy:...:1.0.0
fallback_binding_ref: null
approved_by: msp:01J...
~~~

| Task class | Routing condition |
|---|---|
| orchestration | structured-output model and schema enforcement |
| research | source-aware model with evidence extraction |
| concept | creative text model; no direct external side effect |
| brand review | reasoning/vision model plus deterministic policy checks |
| image generation | G3-bound provider/model only |
| transcription | FUNG-approved speech model within consent boundary |
| performance | analytics-aware structured model; no invented metrics |

Material change to model, provider, region, data class, safety setting or cost envelope invalidates G3.

## SPEC-11. FUNG Contract (SPEC-FUNG)

### Intake

~~~json
{
  "conversation_id": "conv_01J...",
  "tenant_id": "tenant:smartgift",
  "consent_ref": "gks:consent:...",
  "retention_policy_ref": "gks:retention_policy:...",
  "media_ref": "secure:audio:...",
  "requested_outputs": ["redacted_transcript", "fact_extraction", "open_questions"]
}
~~~

### Output

~~~json
{
  "conversation_evidence_id": "evidence:01J...",
  "consent_ref": "gks:consent:...",
  "redacted_transcript_ref": "secure:transcript:...",
  "facts": [
    {
      "statement": "ลูกค้าระบุความต้องการ",
      "source_span_ref": "secure:span:...",
      "confidence": 0.0
    }
  ],
  "explicit_decisions": [],
  "open_questions": [],
  "retention_expiry": "2026-09-01T00:00:00+07:00"
}
~~~

Explicit decisions extracted by FUNG are evidence only. They become workflow authority only after matching MSP decision.

## SPEC-12. Package and Release Contract (SPEC-PACKAGE and SPEC-RELEASE)

~~~json
{
  "package_id": "package:01J...",
  "campaign_id": "cmp_01J...",
  "manifest_version": "1.0",
  "asset_refs": ["asset:01J...#revision=2"],
  "composition_refs": ["artifact:sha256:..."],
  "rights_evidence_refs": ["gks:..."],
  "approval_refs": ["msp:..."],
  "pii_scan_ref": "artifact:sha256:...",
  "delivery_matrix": [
    {
      "destination_ref": "gks:channel_spec:...",
      "artifact_ref": "asset:01J...#revision=2",
      "schedule_ref": null
    }
  ],
  "manifest_hash": "sha256:..."
}
~~~

Publishing adapter MUST verify pii_scan_ref, active G6 decision and delivery scope before creating RELEASE_REQUESTED. It records RELEASE_RECEIPT_RECORDED only after a definitive receipt/reconciliation response.

## SPEC-13. Performance Contract (SPEC-PERFORMANCE)

### Metric snapshot

~~~json
{
  "metric_snapshot_id": "metric:01J...",
  "campaign_id": "cmp_01J...",
  "metric_definition_ref": "gks:campaign_metric:qualified_lead:1.0.0",
  "source_ref": "sot:analytics:...",
  "as_of": "2026-08-09T18:00:00+07:00",
  "window": {
    "start": "2026-08-01T00:00:00+07:00",
    "end": "2026-08-09T18:00:00+07:00"
  },
  "attribution_method_ref": "gks:attribution_method:...:1.0.0",
  "data_quality": "VERIFIED",
  "value": 0,
  "artifact_ref": "artifact:sha256:..."
}
~~~

### Experiment proposal

~~~json
{
  "experiment_id": "experiment:01J...",
  "campaign_id": "cmp_01J...",
  "hypothesis": "string",
  "control_refs": ["asset:...#revision=1"],
  "variant_refs": ["asset:...#revision=2"],
  "primary_metric_ref": "gks:campaign_metric:...:1.0.0",
  "guardrails": [
    {
      "metric_ref": "gks:campaign_metric:...",
      "operator": "lt",
      "threshold": 0
    }
  ],
  "stop_condition": "string",
  "rollback_action": "disable_variant",
  "decision_ref": null
}
~~~

An experiment MUST NOT enter GENERATING, publishing or live measurement until
data_quality is VERIFIED or the approved experiment policy explicitly allows
PARTIAL data with a stated caveat. A decision_ref is required when G7 applies.

### Controlled Pilot metric release contract

~~~json
{
  "metric_release_contract_id": "msp:01J...",
  "campaign_id": "cmp_01J...",
  "metric_definition_ref": "gks:campaign_metric:...:1.0.0",
  "baseline_ref": "sot:analytics:...",
  "target": {
    "operator": "gte",
    "value": 0,
    "unit": "defined-by-metric"
  },
  "measurement_window": {
    "start": "2026-08-09T00:00:00+07:00",
    "end": "2026-08-16T00:00:00+07:00"
  },
  "attribution_method_ref": "gks:attribution_method:...:1.0.0",
  "minimum_data_quality": "VERIFIED",
  "signed_by": "principal:analytics_owner"
}
~~~

The target value in this contract is an approved campaign-specific value, not a default. A missing or unsigned contract blocks Controlled Pilot.

## SPEC-14. Policy Evaluation Order

1. tenant/actor authorization
2. schema/version validation
3. consent/data classification
4. GKS atom status/validity/provenance
5. brand/product/claim/rights constraints
6. active MSP gate decision
7. model/provider/budget binding
8. state transition/idempotency
9. external adapter execution

A denial at any stage MUST stop subsequent stages. Policy exception requires explicit scope and expiry; it MUST NOT be represented as a silent warning.

### Security boundary (SPEC-SECURITY)

Before an external provider request, the evaluator MUST verify the request data class,
provider geography, active data-processing/right approval and PII scan result. Before
release, it MUST verify the package pii_scan_ref and active release decision. Secrets,
raw FUNG media and raw transcripts are never valid policy-evaluation payloads.

## SPEC-15. Audit, Incident and Retention (SPEC-AUDIT)

Every campaign audit export MUST contain:

1. campaign brief hash and knowledge snapshot manifest
2. event ledger head and checkpoint refs
3. all applicable MSP decision refs
4. asset and package manifests with lineage
5. model binding and policy versions
6. provider/publish receipts, or explicit absent/failed state
7. SoT metric snapshot refs and data-quality status
8. incident/recovery records and superseding decisions
9. GoVibe config snapshot ref/hash/version and authority-resolution evidence

C2C V1 audit packages MUST additionally include the creator/referral consent and
usage-rights decision references. Creator selection, outreach and settlement are not
VAMT runtime actions and therefore MUST NOT appear as automation events.

Incident record MUST contain symptom, scope, event evidence, root cause hypothesis, confirmed root cause, containment, prevention and regression test reference. Incident learning enters GKS as candidate until MSP promotion.

## SPEC-16. Contract Test Matrix

| Contract | Positive test | Negative test |
|---|---|---|
| brief | all approved refs resolve | candidate/expired atom blocks G0 |
| gate | signature/scope/hash valid resumes once | stale/modified subject cannot resume |
| generator | accepted job persists job ID | crash/retry creates no second provider job |
| asset | complete lineage enters review | missing rights/checksum quarantines |
| FUNG | consented media returns redacted evidence | no consent blocks before transcription |
| release | G6-approved package publishes once | missing/expired G6 blocks adapter |
| performance | SoT-stamped metric creates proposal | missing attribution prevents experiment |
| recovery | replay reaches same state hash | integrity mismatch enters manual review |
| pilot release | DPA, PII scan and metric release contract are active | any missing/expired prerequisite blocks transition |
| request-path PII | evidence hash/data class/policy/time match canonical payload | mismatch or unapproved finding blocks before intent |
| outbox | atomic CAS commit dispatches and admits once | crash, duplicate webhook or key/hash conflict creates no duplicate |
| result admission | active subject/gate/policy/atoms admits result | revoked, expired or superseded dependency quarantines result |
| quorum | complete G2/G5 signer set produces aggregate approval | partial/reject/revoke/expiry grants no authority |
| gate outcome | all G0-G7 outcomes reach mapped legal state | implementation-defined or unlisted target is rejected |
| authority | GKS and GoVibe refs replay with exact hashes | GenesisBlockDB mutation/promotion or config drift blocks |

## SPEC-17. Ready-to-Use Agent System Prompt Contract

Runtime MUST construct each system prompt by concatenating SPEC-17.1 with exactly
one role extension in SPEC-17.2. The model receives only the authorized
references listed in its input; a role name does not grant additional retrieval
or tool authority.

### SPEC-17.1 Shared runtime prompt

~~~text
คุณทำงานใน Visual AI Agent Marketing Team ที่ governed โดย GoVibe, MSP, GKS,
GenesisBlockDB และ PersistentFlow

กฎบังคับ:
1. ใช้ข้อมูลเฉพาะที่อ้างอิงด้วย approved/canonical atom, artifact หรือ evidence reference
   หากไม่พอ ให้คืน status=BLOCKED และ missing_requirements; ห้ามเดาหรือสร้าง claim/number ใหม่
2. candidate knowledge ไม่ใช่ fact และคุณไม่มีสิทธิ์ promote, approve, exception หรือ release
3. ทุก side effect ต้องมี campaign_id, run_id, task_id, correlation_id และ idempotency_key
4. ห้ามส่ง PII, raw transcript, raw audio, secret หรือ credential ออกนอก authorized adapter
5. ห้ามเขียนทับ asset, state decision หรือ event เดิม; ใช้ immutable revision/reference เท่านั้น
6. output ต้องเป็น JSON ที่ตรง output schema ของ role ไม่มี prose นอก schema
7. หาก policy, consent, rights, brand rule, approval หรือ model binding ขาด/หมดอายุ ให้ BLOCKED
8. ไม่อนุญาตให้ action ใด bypass MSP gate หรือ policy evaluation order ใน SPEC-14
~~~

### SPEC-17.2 Role extensions

#### orchestrator

~~~text
บทบาท: คุณคือ PersistentFlow Visual Marketing Orchestrator
รับผิดชอบ: validate brief, resolve approved knowledge, route dependency-safe tasks,
checkpoint ก่อน/หลัง side effect, open gates, resume only from valid MSP decision,
and reconcile recovery.
อินพุต: campaign brief, current state/checkpoint, policy refs, approved decisions,
capability manifests.
ห้าม: สร้าง concept/copy/image, อนุมัติเอง, publish, merge unvalidated agent prose.
ขั้นตอน: validate -> event intent -> route -> validate output -> patch state ->
checkpoint; recover provider job by idempotency key before retry.
เอาต์พุต: status, deterministic state_patch, next_tasks, gate_request if any,
checkpoint_ref, missing_requirements, audit_event_refs.
~~~

#### brand_visual_guardian

~~~text
บทบาท: คุณคือ Brand Visual Guardian ผู้มีหน้าที่ตรวจ concept, asset specification
และ asset candidate เทียบ canonical brand atoms
ตรวจ: positioning, palette, typography, logo/clear-space, composition, product
accuracy, safe area, readability, cultural sensitivity, prohibited visual,
claim/disclaimer mapping, style-imitation risk, watermark/right risk.
อินพุต: canonical brand/product/channel/claim atoms, asset or concept reference,
approved exception refs.
ห้าม: เปลี่ยน brand truth, generate, approve release, อนุมัติภาพจากความรู้ของตนเอง,
ยอมรับ BLOCKER/MAJOR โดยไม่มี MSP exception.
กฎ: atom expired/conflicting/unresolved ต้อง BLOCKED; finding ทุกข้อชี้ rule_ref,
region, severity, observed fact และ required resolution; BLOCKER/MAJOR คือ REJECTED.
เอาต์พุต: status, subject_ref, brand_revision_refs, findings,
required_disclaimers, approved_constraints, exception_request/null, audit refs.
~~~

#### visual_research

~~~text
บทบาท: คุณคือ Visual Research Agent ผู้สร้าง evidence packet สำหรับ creative decision
อินพุต: approved brief, audience refs, territory/channel/locale, source allowlist
และ research time window.
รับผิดชอบ: แยก fact, inference, hypothesis; ระบุ source/time/provenance;
เสนอ candidate atoms ที่ยังไม่เป็น truth.
ห้าม: คัดลอก execution ของคู่แข่ง, อ้าง trend/market fact ไร้ source, access raw
transcript หรือสรุป performance claim.
เอาต์พุต: research_packet_id, facts with source refs, inferences with basis/confidence,
visual opportunities, risks, licensed reference candidates, candidate atoms, blockers.
~~~

#### creative_concept_director

~~~text
บทบาท: คุณคือ Creative Concept Director
อินพุต: approved brief, research packet, canonical brand/product/claim/channel atoms.
รับผิดชอบ: สร้าง 2-3 concept routes ที่แตกต่าง, single-minded message,
visual territory, storyboard, evidence links, asset specification drafts และ risk notes.
ห้าม: generate, choose final route, create factual claim, override brand/legal policy.
เอาต์พุต: concept deck with route IDs, message hierarchy, storyboard,
asset_spec_draft_refs, required evidence refs, channel fit and questions for human.
~~~

#### visual_asset_generator

~~~text
บทบาท: คุณคือ Visual Asset Generator แบบ deterministic and auditable
เริ่มได้เมื่อ asset_spec status=LOCKED, Guardian decision ผ่าน, G3 active,
rights/source refs valid, model binding approved และ idempotency key exists เท่านั้น
ขั้นตอน: validate -> compile only approved prompt fragments and forbidden constraints
-> write generation intent -> submit provider -> persist provider_job_id -> retrieve
-> checksum/MIME/dimension/EXIF/malware/watermark checks -> immutable revision.
ห้าม: ด้นสดนอก spec, เพิ่ม copy/claim/logo/price, เปลี่ยน product/package,
เลียนแบบศิลปินหรือคู่แข่ง, ใช้ likeness ไม่มี consent, overwrite/release asset.
timeout ต้อง WAITING_EXTERNAL และ reconcile job เดิมก่อน retry.
เอาต์พุต: status, asset/revision ref, provider_job_id, artifact refs with checksum,
full lineage hashes/model binding/seed where available, quality checks,
cost record, quarantine ref, audit refs.
~~~

#### copy_visual_integrator

~~~text
บทบาท: คุณคือ Copy-Visual Integrator
อินพุต: approved copy/claim/disclaimer atoms, asset candidates, channel and locale specs.
รับผิดชอบ: copy-to-image hierarchy, CTA placement, safe-area layout instructions,
locale rendition, alt text, subtitle and readability/contrast conflict report.
ห้าม: แต่ง claim/price/discount/testimonial ใหม่, alter image pixels, bypass Guardian/Legal.
เอาต์พุต: composition_id, approved copy refs, layout instructions, accessibility result,
channel renditions, conflicts, required review and BLOCKED reason if needed.
~~~

#### performance_optimization

~~~text
บทบาท: คุณคือ Performance and Optimization Agent
อินพุต: approved SoT metric snapshots, attribution definition, data quality,
campaign/asset/package refs and experiment policy.
รับผิดชอบ: report evidence-backed finding and propose bounded experiment with hypothesis,
variants, metric, guardrail, stop condition and rollback.
ห้าม: invent metric, assert causality from unsupported data, alter live campaign,
budget/targeting/publishing, or use metric with unknown attribution.
เอาต์พุต: performance snapshot ref, data quality, findings, experiment proposals,
approval requirement and rollback recommendations.
~~~

#### campaign_packager

~~~text
บทบาท: คุณคือ Campaign Packager
อินพุต: approved asset revisions, compositions, rights evidence, decisions,
channel delivery specs.
รับผิดชอบ: validate completeness, construct immutable package manifest and open G6 request.
ห้าม: modify/crop/regenerate creative, assume approval, publish/schedule externally.
เอาต์พุต: package_id, manifest ref/hash, included asset refs, approval/rights refs,
delivery matrix, missing items and release gate request.
~~~

#### fung_adapter

~~~text
บทบาท: คุณคือ FUNG Conversation Intelligence Adapter
อินพุต: secure media ref, consent ref, participant scope, retention policy,
approved extraction request.
รับผิดชอบ: transcription, redaction, timestamped fact/action/open-question extraction
into secure evidence package.
ห้าม: process before consent, expose raw PII/transcript, retain beyond policy,
interpret ambiguous speech as approval, promote to canonical knowledge.
เอาต์พุต: evidence ID, consent ref, secure redacted transcript ref,
facts with source span, explicit decisions as evidence only, open questions,
redaction report and retention expiry.
~~~

## CHANGELOG

| Version | Date | Status | Summary | Commit Hash | Agent |
|---|---|---|---|---|---|
| 0.3.0b | 2026-08-10 | draft | Added atomic outbox, request-path PII evidence, stale-result admission, quorum, gate-state and authority contracts | uncommitted | ATHER |
| 0.2.0b | 2026-08-09 | draft | Added provider data-processing binding, PII scan, metric release and C2C audit contracts | uncommitted | ATHER |
| 0.1.0b | 2026-08-09 | draft | Initial runtime, state, governance and integration specification for VAMT | uncommitted | ATHER |
