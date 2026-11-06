# ProofLens Architecture & Design Specification

## 1. System Overview

ProofLens is an evidence-first, reviewer-controlled investigation workspace for financial document packets (loan applications, salary slips, and bank statements). Rather than issuing opaque authenticity scores or certifying fraud, it extracts source-grounded claims, aligns semantic contexts, cross-checks visible rendering against native PDF streams, computes deterministic financial reconciliation, and outputs an immutable, traceable dossier.

```
                          [ Client Layer (Vite + React + TS) ]
          (Enterprise Investigation: Soft-Grey Canvas #F8FAFC, Dark Slate #0F172A, Indigo #4F46E5, 3-Panel Workspace)
       +--------------------------------------------------------------------------+
       | [Documents Navigation (20%)] | [Source Viewer (50%)] | [Findings (30%)]   |
       |  - Packet Checklist          |  - PDF.js Overlays    |  - Typed Findings |
       |  - Page Thumbnails           |  - Dual Compare Crops |  - Revisions Form |
       +--------------------------------------------------------------------------+
                                         │  (REST API / OpenAPI)
                                         ▼
                               [ FastAPI Backend ]
       +--------------------------------------------------------------------------+
       | /cases  | /documents  | /runs  | /fields  | /findings  | /reports | /audit |
       +--------------------------------------------------------------------------+
               │                                                  │
               ▼                                                  ▼
     [ Persistent Storage ]                             [ Processing Pipeline ]
    - SQLite (WAL Mode)                                 (Worker / Local Queue)
    - Original Uploads (SHA-256)                        ┌────────────────────────┐
    - Derivatives (Crops, Previews)                     │ 1. Ingestion & Hash    │
    - Audit Trail (Canonical JSON)                      │ 2. Page Render & Route │
                                                        │ 3. Native & OCR Parser │
                                                        │ 4. Stream Cross-Check  │
                                                        │ 5. Financial Engine    │
                                                        │ 6. Visual Forensics    │
                                                        │ 7. Bounded Agent (Cop) │
                                                        │ 8. Immutable Dossier   │
                                                        └────────────────────────┘
```

---

## 2. Enterprise Investigation & Multi-Document Reconciliation Design System Specification

In accordance with user directives and industry enterprise benchmarks (Thoropass compliance suite, Draftable document comparator, and modern transaction reconciliation workspaces), ProofLens features a high-density, professional investigative workspace.

### 2.1 Color Tokens

| Token Name | Hex Code | Purpose & Usage |
| :--- | :--- | :--- |
| `--surface-canvas` | `#F8FAFC` | Soft-grey canvas background for clean readability and reduced eye strain. |
| `--surface-card` | `#FFFFFF` | Crisp white card surface, elevated with subtle slate border `#E2E8F0`. |
| `--surface-dark` | `#0F172A` | Deep dark slate for persistent left sidebar, badges, and high-contrast accents. |
| `--surface-subtle` | `#F1F5F9` | Slate-100 for secondary badges, input backgrounds, and toolbar controls. |
| `--text-primary` | `#0F172A` | Dark slate typography for high readability across data tables. |
| `--text-secondary` | `#475569` | Slate-600 for descriptions, secondary metrics, and field notes. |
| `--text-muted` | `#64748B` | Slate-500 for small-caps tags, timestamps, and column headers. |
| `--primary-action` | `#4F46E5` / `#6366F1` | Indigo / muted violet for primary pipeline triggers, active selections, and focus rings. |
| `--semantic-red` | `#EF4444` / `#FEE2E2` | Red for discrepancies, arithmetic mismatches, and unreconciled exceptions. |
| `--semantic-amber`| `#F59E0B` / `#FEF3C7` | Amber for warnings, candidate split-matches, and items needing reviewer attention. |
| `--semantic-emerald`| `#10B981` / `#D1FAE5` | Emerald for verified checksums, reconciled ledgers, and healthy controls. |

### 2.2 Typography Hierarchy

- **Font Stack:** Inter, system sans-serif (`"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`).
- **Main Headings:** Crisp sentence case with tight tracking (`Program & Reconciliation Overview`, `3-Panel Investigation Workspace`).
- **Captions & Categories:** Tracked uppercase small-caps (`text-[10px] uppercase font-bold tracking-wider text-slate-400`).
- **Data & Arithmetic:** Monospaced formatting for currency numbers, hashes, and bounding box coordinates (`JetBrains Mono`, `ui-monospace`).

### 2.3 Modular Investigation Workspace Architecture

The workspace is organized into a persistent navigation structure and a 3-panel synchronized investigation stage:
1. **Persistent Left Sidebar (`w-64` / `w-16` collapsed):** Dark slate `#0F172A`, housing case context, navigation views, and reviewer status.
2. **Top Navigation Header (`h-16`):** Breadcrumbs, global search, sensitivity threshold slider, and primary action triggers.
3. **Panel 1: Documents & Extracted Packet Claims (`w-80`):** Accordion document file selector, filter tabs (All, Discrepancies, Matched, Warnings), and claim items.
4. **Panel 2: Evidence Viewer (`flex-1`):** Draftable-inspired side-by-side document comparator, zoom controls, sync scroll lock, bounding box highlights, minimap diff gutter, and bottom dual-crop raster alignment inspector.
5. **Panel 3: Findings & Quick View Inspector (`w-96`):** Transaction quick view drawer with visual reconciliation match status node tree (root claim -> salary slip -> bank credit -> split candidate), structured audit table, non-accusatory alternative hypotheses, and sovereign reviewer disposition controls.

- **Extra-Rounded Radii:** Cards use `rounded-3xl` (24px) or `rounded-2xl` (16px), giving a soft, tactile presence.
- **Pill Action Buttons:** High-contrast pill buttons (`rounded-full py-2.5 px-6 font-medium bg-[#121212] text-white hover:bg-neutral-800`).
- **Tactile Sliders & Strips:** Horizontal pill selectors for case documents/dates, smooth pill-track sliders for sensitivity or zoom thresholds.
- **Floating Action Touchpoints:** Prominent dark circular icon buttons for primary actions (`rounded-full w-12 h-12 bg-black text-white`).

---

## 3. Storage & Separation of Derivatives

```
C:\Users\Aniket\.gemini\antigravity\scratch\ProofLens\
├── storage/
│   ├── originals/            # Immutable raw uploads named by UUID (never edited)
│   ├── derivatives/
│   │   ├── pages/            # Rendered high-res PNGs per page (e.g., page_001_300dpi.png)
│   │   ├── crops/            # Evidence crops for viewer & model evaluation
│   │   └── previews/         # Web-optimized lightweight preview assets
│   ├── reports/              # Frozen PDF dossiers & JSON evidence manifests
│   └── checkpoints/          # Retained offline cryptographic audit checkpoints
```

---

## 4. Work Queue & Windows Fallback Architecture

To handle expensive document operations without freezing request handlers:
1. **Linux / WSL2 / Docker Environment:** Celery + Redis worker pool.
2. **Native Windows Environment (Current Host):** A resilient, separate-process persistent job runner (`backend/worker/local_runner.py`) polling the SQLite queue table with transaction-safe state locking, retry backoff, and idempotent stage keys.

