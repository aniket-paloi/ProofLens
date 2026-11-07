# ProofLens — Final blueprint and Antigravity implementation prompts

Prepared for Aniket Paloi. Final research review: 3 November 2026.

## Final decision

**ProofLens: Evidence-Driven Document Investigation.**

Tagline: Don't Just Verify Documents. Investigate the Evidence.

Build a reviewer-controlled financial-document investigation workspace. It extracts source-linked facts, compares compatible claims, inspects visual irregularities, checks legitimate explanations, and creates a traceable dossier. It does not certify authenticity, establish fraud, contact issuers without an implemented integration, or reject applicants.

This is the final consolidated specification. It supersedes earlier V2/V2.1 wording where choices differ. It contains a complete plan and 23 ordered copy-and-paste prompts, not a completed application, trained model or reproduced benchmark result. Further features are added only when required by the problem statement, a demonstrated failure or an explicitly requested extension.

## Start in Antigravity

1. Create/open the ProofLens folder. If code already exists, inspect and preserve it.
2. Put the supplied problem statement at docs/problem-statement.pdf.
3. Put this file in the project root as ProofLens_Antigravity_Prompt_Pack.md.
4. Paste the startup prompt below. Then execute one numbered milestone at a time.
5. Accept a milestone only when its stated checks have actually run or it is honestly recorded as incomplete.

```text
Read ProofLens_Antigravity_Prompt_Pack.md and docs/problem-statement.pdf.
Use this final specification. If code already exists, inspect its actual behavior,
map implemented milestones by title, and preserve working functionality and data.
Do not restart or overwrite the project. Otherwise execute Prompt 00 only.
Keep root AGENTS.md short and link to the detailed contracts here.
Execute only the next incomplete milestone. Verify its acceptance conditions.
Report changed files, actual commands/results, blockers, and the next step.
Never fabricate repository audits, training artifacts, inference or passed tests.
```

The coding agent in Antigravity builds the app. The investigation agent described below is a separate, constrained runtime feature. IDE access does not grant API credits to your app. Do not paste the full pack into persistent rules: reference this file and read the current milestone.

## Frozen product scope and differentiation

Primary reviewer: a human investigating a fictional loan application packet: application form, three monthly salary slips and a covering bank statement. Input: PDFs, PNG/JPEG; English printed documents. Initial format/layout coverage is declared and tested. Additional languages, handwriting, signature authentication, external bank/identity verification and arbitrary documents are unsupported until separately implemented/evaluated.

The differentiating workflow has six parts:

1. Typed claims align applicant, period, currency, unit and gross/net salary meaning before comparison.
2. Visual and contextual observations connect to inspectable evidence rather than an unexplained fraud percentage.
3. Alternative checks consider OCR ambiguity, split/delayed payments, period mismatch and incomplete coverage.
4. Provenance distinguishes known derivation from unknown independence; agreeing values are not automatic independent confirmation.
5. Reviewer corrections propagate through dependent checks while preserving original extraction and old reports.
6. Coverage, limitations and scoped negative evidence remain visible beside findings.

These are defensible implementation differentiators, not claims of global novelty. Similar prototypes exist. Winning cannot be guaranteed; reliability, demonstrated requirements coverage and measured results determine the strength of the entry.

## Final architecture and technology decisions

Use one modular application, not a fleet of separate microservices.

| Layer | Final implementation | Why / boundary |
| --- | --- | --- |
| Development | Google Antigravity | Sequential milestones and short root AGENTS.md |
| Frontend | React, TypeScript, Vite | Typed application UI |
| UI | Tailwind and accessible shadcn/ui components (Stoic iOS monochrome aesthetic) | Consistent reviewer workspace; no generic blue AI templates |
| Viewer | PDF.js plus geometry overlays | Original page and evidence inspection |
| Graph | React Flow read projection; optional NetworkX traversal | Source-linked claim graph, no graph database |
| API | FastAPI, Pydantic | Validated contracts and case-scoped access |
| Persistence | SQLAlchemy, Alembic, SQLite initially | Versioned records and migrations |
| Original storage | Private local files, separate derivatives | Original byte integrity and controlled access |
| Work queue | Redis/Celery inside Linux Docker/WSL2 | Bounded expensive processing, concurrency one initially |
| Queue fallback | Separate-process persistent local runner | Native Windows fallback behind same queue contract |
| Native PDF | PyMuPDF | Text/spans/fonts/positions; review AGPL/commercial terms |
| Raster OCR/layout | PaddleOCR plus selected PP-StructureV3 modules | Words, regions and tables; disable unrelated modules |
| Visual baseline | OpenCV plus PDF properties | Explainable local observations |
| Trained model | PyTorch/Torchvision MobileNetV3 Small region baseline | Feasible fine-tuning; no claim of pixel localization |
| Financial logic | Python Decimal and typed comparisons | Reproducible calculations |
| Agent | Persisted typed state machine, seven allowed tools | Bounded checks and actual execution history |
| Language model | Optional backend Gemini structured-output adapter | Context mapping/explanation, semantic validation required |
| Reports | ReportLab PDF plus JSON evidence manifest | Frozen investigation snapshot |
| Verification | pytest and Playwright | Meaningful backend and browser journeys |

## Final feature tiers: all 18 proposed features accounted for

| Proposed feature | Final tier and implementation boundary |
| --- | --- |
| 1 Ingestion | Core: validation, originals, hashes, page-level routing, bounded jobs |
| 2 Extraction | Core: real fields, token/cell geometry, run/revision references, genuine scores |
| 3 Structure | Core for declared layouts: fields, tables, missing/unknown structures |
| 4 Visual forensics | Core explainable baseline; trained region model included in full build, advanced segmentation optional |
| 5 Contradiction engine | Core: only aligned typed claims can contradict |
| 6 Reconciliation | Core: Decimal, constrained salary matching, explicit coverage and assumptions |
| 7 Evidence graph | Core compact view after clickable evidence works; ordinary tables remain authoritative |
| 8 Independence/provenance | Core known lineage and unknown default; no unsupported common-origin inference |
| 9 Alternatives | Core applicable checks, recorded outcomes, remaining uncertainty |
| 10 Fusion | Core evidence bundles with separate signals, not an authenticity probability |
| 11 Coverage | Core lifecycle/applicability/outcome matrix with uninspected regions |
| 12 Copilot | Full prototype: bounded actual tools and optional evidence-grounded LLM explanation |
| 13 Memory | Core typed state, versioned inputs, actual tool calls and stop reasons |
| 14 Corrections | Core immutable revisions, dependency recomputation, history |
| 15 FraudSim | Bonus after core: isolated fictional lab, labels withheld from inference |
| 16 What-if | Bonus: separate hypothetical branch, never original evidence |
| 17 Feedback analytics | Bonus: descriptive reviewer metrics, no automatic retraining |
| 18 Integrity timeline | Core history; hash chain checked against separately retained checkpoint with limits |

## Precise investigation semantics

A salary slip showing 75,000, a bank credit showing 42,000 and an application showing 90,000 do not automatically contradict. First align person, salary basis, time period, currency and annual/monthly meaning. A bank statement transaction may include allowances, deductions, reversals or delayed payment; unsupported interpretation remains unknown.

Searches returning no match are phrased as “not found in the submitted pages and selected period,” not “payment did not happen.” Statement numbering and opening/closing balances are indicators, not proof of complete acquisition.

Preserve method-specific extraction score, model score, measured visual property, severity, evidence strength, uncertainty and reviewer status as separate attributes. Do not multiply correlated probabilities or count multiple detectors of one crop as independent confirmation.

A PDF's selectable text may be stale, hidden or different from visible rendering. Re-OCR important rendered regions independently and show disagreement with native extraction. Normal searchable scans often have invisible OCR text; that property alone is not malicious. Neither extraction branch is guaranteed truth.

Provenance status: unknown; known shared source; possible shared source with a stated basis; independent acquisition supported by acquisition records. The last does not establish independently created facts. Reliability and source lineage are distinct.

## Final data model

Use UUIDs, UTC timestamps, database foreign keys, case authorization and optimistic revision checks. Enable SQLite foreign keys. Preserve originals and original extraction rows; never overwrite old reports after corrections.

| Group | Entities and required concerns |
| --- | --- |
| Case/access | Case; minimal local reviewer User/Session for full app; audit actor identity and case access |
| Sources | Document, Page, source tokens/cells; original hash, private paths, geometry and transforms |
| Facts | Field, FieldRevision, Claim, Transaction; raw/normalized values and financial semantics |
| Checks | CheckDefinition, CheckExecution; applicability, lifecycle, result, coverage, assumptions, versioned inputs |
| Observations | VisualObservation; method/version, measured property, source/comparison regions and limits |
| Evidence | EvidenceEntity or typed junctions, EvidenceLink, Relationship, ProvenanceAssertion; enforce valid references |
| Execution | ProcessingRun, InvestigationState, ToolExecution; document snapshot, input fingerprints, versions, actual outcomes |
| Review/output | Finding, ReviewAction, ReportArtifact, AuditEvent; dispositions, frozen reports, canonical event hashes |
| Bonus | LabExperiment, SimulationRun; isolated ground truth and hypothetical state |

## API contract

| Method | Path | Contract |
| --- | --- | --- |
| GET | /health/live and /health/ready | Process and actual dependencies/model readiness |
| GET | /capabilities | Implemented/partial/unsupported capabilities and versions |
| POST | /auth/login and /auth/logout | Minimal local reviewer session; credentials never in frontend code |
| POST / GET | /cases | Create/list authorized cases |
| GET | /cases/{case_id} | Summary and latest run references |
| POST / GET | /cases/{case_id}/documents | Upload/list source documents |
| GET | /documents/{document_id}/pages/{page_number} | Authorized derivative and geometry metadata |
| POST | /cases/{case_id}/runs | Create run against immutable document/revision/config snapshot |
| GET | /runs/{run_id} | Actual stages, failures, partial results and retry state |
| GET | /runs/{run_id}/fields | Source-linked fields and current revision references |
| POST | /fields/{field_id}/revisions | Correction with expected revision, actor and reason |
| GET | /runs/{run_id}/findings | Findings and grouped evidence summaries |
| GET | /findings/{finding_id}/evidence | Same-case/run source links and observations |
| POST | /findings/{finding_id}/reviews | Versioned reviewer disposition |
| GET | /runs/{run_id}/graph and /coverage | Read projections from authoritative records |
| POST | /findings/{finding_id}/investigate | Bounded investigation job using current evidence fingerprint |
| POST | /runs/{run_id}/questions | Optional evidence-grounded case Q&A; bounded tool/LLM access |
| POST | /runs/{run_id}/reports | Generate immutable PDF/JSON snapshot |
| GET | /reports/{report_id} | Authorized report metadata/download |
| GET | /cases/{case_id}/audit | History, checkpoint scope and verification state |

## Frontend and UX contract (Stoic iOS Inspired Minimalist Aesthetic)

Navigation: Cases; Investigation with Overview, Documents, Financial, Graph, Coverage, History, Report tabs; Copilot side panel. Optional Lab and Analytics come later.

UI Styling Mandate:
- In accordance with Stoic iOS design on Mobbin, avoid generic blue/indigo AI UI styles.
- Pure black/charcoal (`#121212`, `#18181B`), soft off-white/warm canvas (`#FBFBF9`, `#F4F4F5`), crisp white cards with subtle borders (`#E4E4E7`).
- Generous whitespace, elegant typography with sentence/lowercase bold titles ("meet prooflens.", "good evening.", "investigate."), tracked small-caps ("EVIDENCE DOSSIER").
- Extra-rounded modular cards (`rounded-2xl`, `rounded-3xl`), pill buttons (`rounded-full`), smooth slider and inspection controls.
- Clear, restrained amber/terracotta/crimson indicators for review findings; green for individual check completion, never a blanket authenticity seal.

## Sequential execution index

| Prompt | Milestone |
| --- | --- |
| 00 | Project rules, environment and requirements |
| 01 | Audit existing repositories before reuse |
| 02 | Working skeleton and contracts |
| 03 | Ingestion, page rendering and jobs |
| 04 | Frontend and evidence viewer |
| 05 | Fictional data generator and split manifest |
| 06 | OCR, tables and source-linked extraction |
| 07 | Native text versus rendered evidence |
| 08 | Financial and cross-document intelligence |
| 09 | Visual forensic baseline |
| 10 | Train a small region model |
| 11 | Integrate and evaluate the visual model |
| 12 | Evidence-linked bounded investigation agent |
| 13 | Claim connections, coverage and correction propagation |
| 14 | Claim graph and source-dependency review |
| 15 | Dossier and reproducibility bundle |
| 16 | Integrity timeline and retained checkpoint |
| 17 | System evaluation and honest capability matrix |
| 18 | Packaging, UX verification and final demo |
| 19 | Optional advanced localization and robustness |
| 20 | Optional FraudSim synthetic robustness laboratory |
| 21 | Optional hypothetical investigation branch |
| 22 | Optional reviewer feedback analytics |

