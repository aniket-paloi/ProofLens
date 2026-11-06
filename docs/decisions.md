# ProofLens Architecture Decision Records (ADRs)

## ADR-001: Enterprise Investigation & Multi-Document Reconciliation Workspace UI (Supersedes Stoic Mobile Reference)

- **Context:** While mobile-first minimalist templates emphasize conversational tranquility, complex multi-document loan fraud investigations require dense evidentiary grounding, simultaneous side-by-side document comparison, and visual node reconciliation trees.
- **Decision:** Adopt an enterprise compliance and reconciliation design system benchmarked directly against industry leading interfaces (Thoropass compliance suite, Draftable multi-page document comparator, and modern transaction reconciliation workspaces):
  - **Color Palette:** Soft-grey canvas (`#F8FAFC`), crisp white cards (`#FFFFFF`), slate borders (`#E2E8F0`), dark slate typography (`#0F172A`), indigo/muted violet primary CTA actions (`#4F46E5`), red for discrepancies/exceptions (`#EF4444`), amber for warnings/candidate matches (`#F59E0B`), and emerald for reconciled/verified checks (`#10B981`).
  - **Persistent Left Sidebar:** Collapsible enterprise sidebar with case context, active packet tags, and sovereign reviewer profile.
  - **Three-Panel Investigation Workspace:**
    - Panel 1: Document selector and extracted packet claims list with status filters.
    - Panel 2: Evidence viewer with side-by-side comparison, bounding box overlays, minimap diff gutter, and bottom dual-crop raster alignment inspector.
    - Panel 3: Findings inspector featuring a visual reconciliation match status node tree (root claim -> salary slip -> bank credit -> split candidate), structured audit table, non-accusatory alternative hypotheses, and sovereign reviewer disposition controls.
- **Consequences:** Maximizes reviewer efficiency, supports side-by-side document scrutiny, and provides visual reconciliation node trees without sacrificing aesthetic sophistication.

---

## ADR-002: Modular Monolith Architecture vs. Microservices

- **Context:** Early specifications evaluated multiple microservices (OCR service, fraud service, report service).
- **Decision:** Build a single modular application containing the FastAPI backend, background job runner, and React/Vite frontend.
- **Consequences:** Eliminates distributed transaction failures, network serialization overhead, and deployment friction for local and hackathon evaluation.

---

## ADR-003: Queue Worker Strategy on Native Windows

- **Context:** Celery has formally deprecated and unsupported native Windows worker execution. Running Celery directly on Windows results in instability and process-forking issues.
- **Decision:** Provide a unified queue abstraction (`JobQueueAdapter`). If Docker/WSL2 is active, Celery/Redis can be engaged. For the primary Windows environment, provide a persistent, multi-process SQLite-backed local job runner with transactional stage locks and retry mechanisms.
- **Consequences:** Ensures zero-friction setup on Windows without external dependencies or risky Celery workarounds.

---

## ADR-004: Typed Claim Alignment Before Contradiction Detection

- **Context:** Comparing numerical values across documents (e.g. comparing an annual gross figure on an application form against a monthly net bank deposit) generates false positives and erodes trust.
- **Decision:** Enforce typed claim normalization: every financial claim must declare its subject, period (start/end date), basis (gross salary, net salary, reimbursement), currency, and unit before any comparison rule fires.
- **Consequences:** Eliminates false contradictions caused by differing tax deductions, pay cycles, or currency denominations.

---

## ADR-005: Separate Storage for Originals and Derivatives

- **Context:** Preprocessing images or sanitizing PDFs risks altering forensic signatures (compression artifacts, font metadata, text streams).
- **Decision:** Original file bytes are hashed (SHA-256) upon upload and stored immutably in `storage/originals/`. All rendering, OCR crops, and preview sanitization write exclusively to `storage/derivatives/`.
- **Consequences:** Preserves byte-level chain of custody and ensures raw evidentiary integrity.
