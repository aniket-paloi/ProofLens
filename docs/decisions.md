# ProofLens Architecture Decision Records (ADRs)

## ADR-001: Rejection of Generic "AI-Blue" UI in Favor of Stoic iOS Minimalist Aesthetic

- **Context:** Standard AI-generated prototypes default to saturated blue/indigo color schemes (`#2563EB`, `#4F46E5`), dense microservice dashboards, and visual noise that conveys robotic boilerplate rather than reviewer focus.
- **Decision:** Strictly enforce the design language of **Stoic iOS** (referenced via Mobbin and provided screen captures). The UI adopts warm off-white canvas backgrounds (`#FBFBF9`), deep charcoal elements (`#121212`), high-contrast pill buttons (`rounded-full`), soft rounded cards (`rounded-3xl`), conversational lowercase headers (`meet prooflens.`, `investigate.`), and restrained terracotta/sage status indicators.
- **Consequences:** Provides a serene, human-crafted investigation workspace that reduces reviewer fatigue while elevating evidence clarity.

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

