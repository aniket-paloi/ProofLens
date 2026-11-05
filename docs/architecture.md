# ProofLens Architecture & Design Specification

## 1. System Overview

ProofLens is an evidence-first, reviewer-controlled investigation workspace for financial document packets (loan applications, salary slips, and bank statements). Rather than issuing opaque authenticity scores or certifying fraud, it extracts source-grounded claims, aligns semantic contexts, cross-checks visible rendering against native PDF streams, computes deterministic financial reconciliation, and outputs an immutable, traceable dossier.

```
                          [ Client Layer (Vite + React + TS) ]
          (Stoic iOS Aesthetic: Deep Charcoal #121212, Warm Canvas #FBFBF9, No AI-Blue)
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

## 2. Stoic iOS-Inspired Design System Specification

In strict conformance with the user directive, ProofLens completely rejects generic "AI-blue" dashboard aesthetics (such as standard saturated blue/indigo templates), adopting the minimalist, human-crafted design language of **Stoic iOS** (curated on Mobbin).

### 2.1 Color Tokens

| Token Name | Hex Code | Purpose & Usage |
| :--- | :--- | :--- |
| `--surface-canvas` | `#FBFBF9` | Warm paper/chalk background canvas for light mode. Calming, organic. |
| `--surface-card` | `#FFFFFF` | Primary card background, elevated with fine hairline border `#E8E8E6`. |
| `--surface-dark` | `#121212` | Deep charcoal / near-black for inverted hero cards, key controls, and focus states. |
| `--surface-subtle` | `#F4F4F2` | Secondary badge, date strip, and input background. |
| `--text-primary` | `#18181B` | High-opacity crisp ink for primary typography and titles. |
| `--text-secondary` | `#71717A` | Warm graphite for conversational prompts, explanations, and metadata. |
| `--text-muted` | `#A1A1AA` | Low-opacity graphite for tracked small-caps and timestamps. |
| `--accent-amber` | `#B45309` / `#FEF3C7` | Soft terracotta / amber for investigation alerts and discrepancy indicators. |
| `--accent-emerald`| `#047857` / `#D1FAE5` | Muted sage green for verified check completion (never blanket "fraud-free"). |
| `--accent-rose` | `#B91C1C` / `#FEE2E2` | Restrained crimson for critical mismatch or corrupt document warnings. |

### 2.2 Typography Hierarchy

- **Font Stack:** Apple System Font Stack (`-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Inter", sans-serif`).
- **Main Headings:** Lowercase or conversational sentence case, bold, tight tracking (`meet prooflens.`, `good evening.`, `investigate.`).
- **Subheadings & Questions:** Medium weight, relaxed line-height to feel like a calm reviewer dialogue (`Are these payment periods aligned?`).
- **Captions & Categories:** Tracked uppercase small-caps (`tracking-widest uppercase text-[11px] text-neutral-400`, e.g., `EVIDENCE DOSSIER`, `GET INSPIRED`).

### 2.3 Modular Controls & Cards

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

