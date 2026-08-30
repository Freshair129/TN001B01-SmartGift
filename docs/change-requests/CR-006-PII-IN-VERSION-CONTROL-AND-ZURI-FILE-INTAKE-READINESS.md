---
doc_type: change-request
id: CR-006
status: proposed
version: "1.0.0"
created_at: "2026-08-30T08:20:00+07:00"
updated_at: "2026-08-30T08:20:00+07:00"
owner: "zuri-ai session (Claude)"
origin: "D:\\zuri-ai — written back into this workspace because files are the shared channel"
impacted_domains:
  - data-pipeline
  - crm
  - integration
severity: "blocking"
---

# CR-006 — Customer PII is in version control on a public remote, and what that means for the zuri-ai file intake

## 0. Read this part first

`data-pipeline/01_raw/05_crm_customer_data/` holds three spreadsheets of real
customer data — a contact list for a named legal entity, its quotation report,
and a purchase history keyed per customer with what was bought, when, and for how
much. **They are tracked in git and live on the public remote.**

Verified four ways rather than inferred, on 2026-08-30:

| Check | Result |
|---|---|
| `git check-ignore <file>` | exit **1** — not ignored |
| `git ls-files data-pipeline/01_raw/05_crm_customer_data` | all three listed — tracked |
| `.gitignore` (only one in the tree, 238 bytes) | no rule mentions `data-pipeline` |
| `GET /repos/Freshair129/TN001B01-SmartGift/contents/…` | all three returned |
| `gh repo view … --json visibility` | **`PUBLIC`** |

Last push: `2026-08-30T00:55Z`.

Filenames are not reproduced here on purpose. This document lands in the same
repository, and writing the customer's name into another tracked file would
widen the exposure it reports.

### Why `.gitignore` did not help

A belief on the zuri-ai side was that this data is gitignored. It is not, and the
mechanism is worth stating because it fails silently in both directions:

**`.gitignore` has no effect on a file that is already tracked.** Adding a rule
after the first commit changes nothing — the file keeps being staged, committed
and pushed, while the rule sits in `.gitignore` looking like it works. Here there
is not even a rule to have been added late; no line mentions `data-pipeline` at
all. Either way the check that would report the problem (`git status`) shows
nothing, because a tracked file with no local edits is not "untracked" and not
"modified". Nothing is wrong from the tool's point of view.

## 1. Required actions in this repository, in this order

**Order matters. Step 2 does nothing useful before step 1, and step 3 is a
different decision from both.**

1. **Make the repository private.** One action, no history change, and it stops
   the ongoing exposure while the rest is decided. Do this before reading further.

2. **Untrack the directory, then ignore it.**
   ```bash
   git rm -r --cached "data-pipeline/01_raw/05_crm_customer_data"
   # then add to .gitignore:
   #   data-pipeline/01_raw/05_crm_customer_data/
   git commit -m "chore: untrack customer PII from version control"
   ```
   Adding the `.gitignore` line alone will not untrack anything. The `git rm
   --cached` is what does it; the ignore rule is what stops it returning.

3. **Decide about history separately, and treat it as a real decision.** A commit
   that deletes the files does not remove them from history — anyone can still
   read them at an earlier commit. Removing them for real means rewriting history
   (`git filter-repo` or equivalent), which is destructive, invalidates every
   existing clone, and is the data owner's call, not an agent's. **This CR does
   not perform it and does not recommend doing it unattended.**

4. **Treat the data as disclosed, not merely at risk.** The repository was public
   and was pushed to this morning. Forks, GitHub's own caches, and any clone taken
   in that window are outside the reach of a later deletion. Whatever notification
   or record-keeping obligation applies to that is a business decision; this
   document only establishes that the window was real.

## 2. Where this data should live instead

The zuri-ai side already holds the destination this data belongs in, and the
architecture there is not the problem — the repository state is.

Customer records belong in zuri-ai's CRM domain, behind its scope chain
(Tenant → Business → Workspace), with the PDPA consent attestation that
`FR-103`/`SEC-005` require and the audit trail every write there produces.
`docs/references/schema-zuri-ai.md` in this workspace already describes those
models.

That makes the spreadsheets in `01_raw/` an **intake artifact** — the input to an
ingestion, not a store of record. Once ingested they have served their purpose,
and the correct end state is: the CRM database holds the data, and version
control holds none of it. That is what step 1.2 above produces.

## 3. Readiness as a file-system intake for zuri-ai — not yet, and the blocker is §0

CR-004 proposes binding this repository to zuri-ai and surfacing its tree in a
Files tab, with GitHub webhook sync and an in-app previewer.

**The directory structure is genuinely well suited to it.** `01_raw` →
`02_prepared` → `03_staging_sql` → `04_review_reports` is a legible lane
progression that maps onto what CR-003 describes, `vaults/` carries real
GenesisBlockDB state, and the provenance artifacts in `04_review_reports`
(`provenance_audit_log.jsonl`, `catalog_version_diff_report.json`) are exactly the
evidence a governance dashboard would want to show. Nothing about the layout is
the obstacle.

**The obstacle is that the tree currently contains customer PII.** A Files tab
that renders this repository would pull that data into zuri-ai through a path
with no consent record, no tenant scoping, and no audit event — bypassing the
controls zuri-ai built for exactly this class of data. It would be a second way
into personal data that avoids every rule governing the first way.

So the sequence is: resolve §1, then the intake is a normal integration question
rather than a data-protection one.

Three smaller observations, none of them blocking:

- **Size.** `data-pipeline/` is 112 MB of PDFs and spreadsheets out of 279 MB
  total. A recursive tree fetch and previewer should page rather than load it, and
  the GitHub trees API truncates large trees — worth knowing before building
  against it.
- **`vaults/*/genesis-db/` holds live database state** — `.bin` segments, a WAL,
  a lock file, an open SQLite projection. Rendering those in a file previewer
  produces bytes with no meaning to a reader, and reading a WAL mid-write is worse
  than useless. Exclude the vault directories from any file browser rather than
  letting the previewer discover them.
- **`node_modules/` is 75 MB** and correctly ignored; a tree view driven off the
  filesystem rather than off git would need to exclude it separately.

## 4. An unresolved discrepancy between two repositories, flagged rather than settled

The Cross-Repo Protocol in this workspace's `AGENTS.md` states that
`msp_vault_resolve` belongs to **API-009**, not API-010. Checking both sides
produces a picture neither document alone shows:

- `D:\msp\docs\` contains **only** `API-009-Persistent-Memory-Contract.md`. There
  is no API-010 document there, and **`msp_vault_resolve` does not appear anywhere
  in MSP's docs.**
- zuri-ai's `ADR-022` (approved, 0.2.0b, 2026-08-15) states the opposite mapping
  in its own tree: **API-010 is canonical vault resolution**, API-009 is episodic
  reads and writes, and `src/modules/agent/msp-vault-resolver.js` implements it
  that way.

So the two repositories number these differently, and nobody has reconciled them.
**This CR does not adjudicate that** — MSP's contract is authoritative for MSP's
own tools, and the reconciliation belongs to a session that can change both.

What is not in dispute, and is the part that matters for CR-002: **the tool does
not exist in either contract today.** Introducing it is a wire-contract change
that goes through MSP's own review, whatever number it ends up carrying.

One correction to a note previously written on the zuri-ai side: a review there
observed that `ADR-GKS-BOUNDARY` does not exist *in zuri-ai*, and said so with
that scope, adding that a document held inside the GKS repository could not be
checked from there. **It does exist** — `D:\gks\docs\ADR-GKS-BOUNDARY.md`, along
with `ADR-GKS-ENTITY-RESOLUTION.md`. The Cross-Repo Protocol's citation was
correct and the zuri-ai note should be read as scoped, not as a refutation.

## 5. Non-negotiable invariants

1. **Personal data does not enter version control.** Not in `01_raw`, not in a
   review report, not in a test fixture. The store of record is zuri-ai's CRM
   behind its consent and audit controls.
2. **A file browser over this repository must exclude `vaults/`** — live database
   state is not a document, and reading it during a write is meaningless.
3. **`.gitignore` is not a removal tool.** Any future "we ignored it" claim about
   already-committed data should be verified with `git ls-files` and
   `git check-ignore`, which disagree with each other in exactly the case that
   matters.

## Open questions

1. **Is making the repository private acceptable operationally**, or does
   something depend on it being public? If something does, that dependency needs
   naming before step 1 can happen — and the data still has to come out either
   way.
2. **Has this data already been ingested into zuri-ai's CRM**, or is the
   spreadsheet still the only copy? Step 1.2 removes it from version control, not
   from disk, but the answer decides whether an ingestion has to happen before the
   raw files can be retired.
3. **Which of the other `01_raw` lanes carry personal data?**
   `01_flowaccount_exports` and `03_product_catalogs` were not opened during this
   review — only filenames were read, and only in the CRM lane. Someone who knows
   the contents should say, rather than leaving it to another filename-level guess.
4. **Who reconciles the API-009 / API-010 numbering** between MSP's contract and
   zuri-ai's ADR-022? Until someone does, any CR citing either number is citing a
   document the other side reads differently.
