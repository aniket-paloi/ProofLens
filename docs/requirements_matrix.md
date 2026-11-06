# ProofLens Requirements Traceability Matrix

**Project:** ProofLens — Evidence-Driven Document Investigation  
**Specification Version:** Consolidated Prompt Pack (Prepared 3 November 2026)  
**Status:** Initial Milestone 00 Scoping & Environment Audit

---

## 1. 18 Proposed Features Classification

| Feature ID | Feature Name | Tier | Primary Component | Verification / Test Target | Implementation Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **F01** | Ingestion & Integrity | **Must-Have** (Core) | `backend/ingestion` | Multi-page PDF/image uploads, SHA-256 hash preservation, page routing, derivative generation, file size/pixel bounds. | Not Started |
| **F02** | Source-Linked Extraction | **Must-Have** (Core) | `backend/parsers` | PyMuPDF (native text/spans), PaddleOCR/PP-StructureV3 (raster), token/cell geometry [0,1], confidence scores. | Not Started |
| **F03** | Document Structure & Tables | **Must-Have** (Core) | `backend/parsers` | Declared layouts (application form, 3 salary slips, covering bank statement), cell-to-row/column geometry, missing fields. | Not Started |
| **F04** | Visual Forensics Baseline | **Must-Have** (Core) | `backend/forensics` | Native PDF font/size/baseline analysis, raster sharpness/contrast/background variance, candidate region proposals. | Not Started |
| **F05** | Typed Contradiction Engine | **Must-Have** (Core) | `backend/intelligence` | Aligned claims only: applicant matching, period alignment, currency, unit, gross vs net salary semantics. | Not Started |
| **F06** | Financial Reconciliation | **Must-Have** (Core) | `backend/intelligence` | Decimal arithmetic, salary credit matching in bank statement, split payments, delayed payments, balance checks. | Not Started |
| **F07** | Evidence Graph | **Must-Have** (Core) | `frontend/components/graph` | React Flow read projection from DB evidence links; keyboard-accessible table fallback; click-through to source page. | Not Started |
| **F08** | Provenance & Independence | **Must-Have** (Core) | `backend/evidence` | Track known lineage vs unknown default; prevent false independence assumptions for duplicate numbers. | Not Started |
| **F09** | Alternative Explanations | **Must-Have** (Core) | `backend/intelligence` | OCR ambiguity checks, split/delayed credits, period mismatches, incomplete statement coverage. | Not Started |
| **F10** | Evidence Fusion | **Must-Have** (Core) | `backend/evidence` | Grouped evidence bundles without calculating fake holistic "authenticity percentages" or multiplying correlated scores. | Not Started |
| **F11** | Coverage Matrix | **Must-Have** (Core) | `backend/intelligence` & UI | Explicit lifecycle (not started, running, completed, failed) and outcome (consistent, discrepancy, insufficient, unable). | Not Started |
| **F12** | Investigation Copilot | **Must-Have** (Core) | `backend/agent` | Persisted state machine with 7 strictly whitelisted tools; optional structured Gemini adapter; no arbitrary execution. | Not Started |
| **F13** | Working Memory & Tool State | **Must-Have** (Core) | `backend/agent` | Typed `InvestigationState` and `ToolExecution` persistence; input revision fingerprinting and tool cache invalidation. | Not Started |
| **F14** | Reviewer Corrections | **Must-Have** (Core) | `backend/review` | Immutable `FieldRevision` with actor/timestamp/reason; invalidates dependent checks; preserves original extraction and past reports. | Not Started |
| **F15** | FraudSim Lab | **Bonus** (Post-Core) | `backend/lab` | Isolated synthetic manipulation testbed; ground truth strictly isolated from detector inference. | Deferred |
| **F16** | What-if Analysis | **Bonus** (Post-Core) | `backend/simulation` | `SimulationRun` on hypothetical assertions; completely isolated from official case evidence and reports. | Deferred |
| **F17** | Feedback Analytics | **Bonus** (Post-Core) | `backend/analytics` | Aggregate reviewer disposition counts; no automatic online model retraining. | Deferred |
| **F18** | Integrity Timeline | **Must-Have** (Core) | `backend/audit` | Canonical JSON SHA-256 chained audit events; independently retained offline checkpoint verification. | Not Started |

---

## 2. Core Mandatory Specification Requirements

| Requirement Area | Specification Rule | Component / Contract | Status |
| :--- | :--- | :--- | :--- |
| **UI Aesthetics** | **Strict Mandate:** Enterprise compliance and multi-document reconciliation design system benchmarked on Thoropass, Draftable, and modern transaction reconciliation workspaces. Soft-grey canvas (`#F8FAFC`), crisp white cards (`#FFFFFF`), dark slate typography (`#0F172A`), persistent sidebar (`#0F172A`), indigo/muted violet primary actions (`#4F46E5`), red for discrepancies, amber for warnings, and emerald for verified checks. | `frontend/src/index.css`, Tailwind config, UI components | Completed (Prompts 02 & UI Evolution) |
| **Evidence Viewer** | Desktop-first 3-column workspace (~20% docs, ~50% source viewer, ~30% findings). PDF.js overlays with normalized coordinates. Side-by-side comparison. | `frontend/src/components/viewer` | Planned (Prompt 04) |
| **Native vs Rendered Check** | Render important fields and re-OCR independently; flag discrepancies between selectable text and visible pixels. | `backend/parsers/crosscheck` | Planned (Prompt 07) |
| **Report Generation** | 6-section PDF (ReportLab) and JSON dossier: Overview, Extracted Info, Contextual Analysis, Visual Findings, Evidence Traceability, Limitations. | `backend/reports` | Planned (Prompt 15) |
| **Model Region Baseline** | Torchvision MobileNetV3 Small candidate region classifier trained on synthetic crops; honest fallback if weights not present. | `ml/train.py`, `ml/infer.py` | Planned (Prompt 10-11) |

---

## 3. Hardware, Dependency & Environment Assumptions

- **Host OS:** Windows 11 (AMD64)
- **Node.js Environment:** Node v26.12.0, npm 11.20.0 installed and verified.
- **Python Runtime Strategy:**
  - Python 3.11 / 3.12 64-bit standard Windows installation recommended for compatibility with PyMuPDF, Torch CPU/CUDA, PaddleOCR, and OpenCV.
  - WindowsApps Python 3.13 execution alias currently blocked by Windows ACL restrictions in standard sandbox; requires standard standalone Python installer or isolated virtualenv.
- **Inference Strategy:** CPU-first execution for local demonstration; lightweight architectures (MobileNetV3 Small) to ensure sub-second inference on standard Windows CPU.
- **Queue Worker Strategy:**
  - Standard Celery requires Linux/WSL2/Docker.
  - On native Windows without WSL/Docker access, system utilizes the specified **Separate-Process Persistent Local Runner** implementing the identical asynchronous job contract.
- **External API & Network:**
  - Local-first operation: all core OCR, rule engines, visual checks, and report generation execute 100% locally with zero external network dependencies.
  - Gemini API structured output adapter is strictly opt-in and server-side.

