# ProofLens: Evidence-Driven Document Investigation

> **Tagline:** Don't Just Verify Documents. Investigate the Evidence.

ProofLens is an evidence-first, reviewer-controlled investigation workspace for financial document packets (loan applications, salary slips, and covering bank statements).

---

## Design System: Enterprise Investigation & Multi-Document Reconciliation
In accordance with user design directives and enterprise benchmarks (Thoropass, Draftable comparison viewer, and modern reconciliation workspaces), ProofLens features a high-density, professional investigative interface:

- **Soft-Grey Canvas & Pure Surfaces:** `#F8FAFC` soft-slate background canvas with `#FFFFFF` crisp card surfaces and subtle borders (`#E2E8F0`).
- **Dark Slate Typography:** High-contrast text hierarchy (`#0F172A` slate-900 headlines, `#334155` slate-700 body, `#64748B` slate-500 metadata).
- **Indigo & Muted Violet Primary Actions:** `#4F46E5` primary action buttons, hover states `#4338CA`, and focused navigation rings.
- **Semantic Status Signals:**
  - **Red (`#EF4444` / `#DC2626`):** Discrepancies, arithmetic mismatches, and unreconciled exceptions.
  - **Amber (`#F59E0B` / `#D97706`):** Warnings, split-candidate matches, and checks requiring reviewer attention.
  - **Emerald (`#10B981` / `#059669`):** Reconciled transactions, verified checksums, and healthy controls.
- **Persistent Left Sidebar:** Dark slate enterprise navigation (`#0F172A`) with collapsible state, active case context, status counts, and sovereign reviewer profile.
- **Three-Panel Investigation Workspace:**
  1. **Panel 1 (Left - Documents & Claims):** Submitted document selector, status filter tabs (All, Discrepancies, Matched, Warnings), and extracted packet claims list.
  2. **Panel 2 (Center - Evidence Viewer):** Side-by-side document comparison canvas (Draftable style) with page navigation, zoom, synchronized scroll locking, bounding box overlays, minimap diff gutter, and bottom dual-crop raster alignment inspector.
  3. **Panel 3 (Right - Findings & Reconciliation Inspector):** Transaction quick view with visual reconciliation match status node tree (connecting declared root claims to salary slips and bank credits), structured claim audit table, non-accusatory alternative hypotheses, and sovereign reviewer disposition controls.

---

## Architectural Guarantees & Invariants
1. **Original Byte Preservation:** Original files are stored immutably in `storage/originals/` with SHA-256 hashes. Derivatives (rendered pages, crops, reports) are stored in separate directories.
2. **Deterministic Financial Arithmetic:** Monetary comparisons use Python `Decimal` / integer subunits.
3. **Cryptographic Audit Trail:** Append-only SHA-256 event hash chain in canonical JSON format, verified offline against retained checkpoints.
4. **No Automated Fraud Accusation:** System reports scoped observations and discrepancies; reviewer disposition remains sovereign.

---

## Running the Application

### 1. Backend (FastAPI)
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
- Interactive Swagger API: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health readiness probe: [http://127.0.0.1:8000/health/ready](http://127.0.0.1:8000/health/ready)

### 2. Frontend (Vite + React)
```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```
- Web Application: [http://127.0.0.1:5173/](http://127.0.0.1:5173/)

### 3. Running Backend Tests
```bash
python -m pytest backend/tests/ -v
```

---

## Milestone Progress Matrix
- **Prompt 00:** Project rules, environment inspection & requirements matrix — **COMPLETED**
- **Prompt 01:** Research repositories audit & third-party notices — **COMPLETED**
- **Prompt 02:** Working skeleton, database models & 3-Panel Enterprise Frontend — **COMPLETED**
- **Prompt 03:** Ingestion, page rendering & background jobs — **IN PROGRESS**
