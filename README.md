# ProofLens: Evidence-Driven Document Investigation

> **Tagline:** Don't Just Verify Documents. Investigate the Evidence.

ProofLens is an evidence-first, reviewer-controlled investigation workspace for financial document packets (loan applications, salary slips, and covering bank statements).

---

## Design System: Stoic iOS Aesthetic (Zero AI Blue)
In accordance with user design directives and the [Stoic iOS design reference on Mobbin](https://mobbin.com/apps/stoic-ios-621f0be7-8046-45cd-b667-97add5f9c3c7), ProofLens avoids generic saturated blue/indigo templates, featuring:
- **Warm Canvas:** `#FBFBF9` paper/chalk background canvas.
- **Deep Charcoal & High Contrast:** `#121212` deep ink cards and key actions.
- **Card Modularity:** Soft extra-rounded cards (`rounded-3xl` / 24px).
- **Tactile Reviewer Controls:** Sleek pill-track sensitivity slider, horizontal packet selector strip, and high-contrast pill buttons (`rounded-full`).
- **Restrained Indicators:** Terracotta/amber for unreviewed or conflicting observations, sage green for verified checks.

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


