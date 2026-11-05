# ProofLens File Layout & Dependency Compatibility Plan

## 1. Actionable File Layout

```
ProofLens/
├── AGENTS.md                              # Persistent architectural rules & invariants
├── ProofLens_Antigravity_Prompt_Pack.md   # Complete consolidated prompt pack & specs
├── THIRD_PARTY_NOTICES.md                 # Open source attributions for utilized code
├── README.md                              # Project setup and review documentation
│
├── docs/                                  # Architectural & regulatory documentation
│   ├── problem-statement-note.md         # Record of problem statement source
│   ├── requirements_matrix.md            # Traceability matrix for all 18 features
│   ├── architecture.md                   # System, UI & storage architecture
│   ├── decisions.md                      # Architectural Decision Records (ADRs)
│   ├── progress.md                       # Milestone tracking matrix
│   ├── github_audit.md                   # Research repo audit & license findings
│   └── evaluation.md                     # Measured model & rule benchmark results
│
├── backend/                               # Python FastAPI Modular Monolith
│   ├── app/
│   │   ├── main.py                       # FastAPI entrypoint & middleware
│   │   ├── config.py                     # Environment settings (local defaults)
│   │   ├── database.py                   # SQLAlchemy engine & SQLite WAL config
│   │   ├── models/                       # Database entities
│   │   │   ├── case.py                   # Case, Document, Page
│   │   │   ├── field.py                  # Field, FieldRevision, Claim, Transaction
│   │   │   ├── finding.py                # Finding, EvidenceLink, ReviewAction
│   │   │   ├── check.py                  # CheckDefinition, CheckExecution
│   │   │   ├── observation.py            # VisualObservation
│   │   │   ├── execution.py              # ProcessingRun, ToolExecution
│   │   │   └── audit.py                  # AuditEvent (canonical JSON SHA-256)
│   │   ├── schemas/                      # Pydantic v2 validation contracts
│   │   ├── routers/                      # REST endpoints (/cases, /runs, etc.)
│   │   ├── parsers/                      # Extraction adapters (PyMuPDF, PaddleOCR)
│   │   ├── intelligence/                 # Financial reconciliation & contradiction logic
│   │   ├── forensics/                    # Visual baseline & model region inference
│   │   ├── agent/                        # Persisted state machine with 7 whitelisted tools
│   │   └── reports/                      # ReportLab PDF & JSON dossier exporter
│   ├── worker/                           # Job queue execution
│   │   └── local_runner.py               # Windows-compatible persistent local runner
│   ├── tests/                            # Pytest suite
│   ├── requirements.txt                  # Pinned backend dependencies
│   └── alembic/                          # Database migration scripts
│
├── frontend/                              # React + TypeScript + Vite Application
│   ├── index.html                        # Application root
│   ├── package.json                      # Pinned npm dependencies
│   ├── vite.config.ts                    # Vite build configuration
│   ├── tailwind.config.js                # Stoic iOS monochrome palette configuration
│   └── src/
│       ├── index.css                     # Stoic design tokens & typography
│       ├── App.tsx                       # Root routing & layout
│       ├── types/                        # TypeScript API contracts matching Pydantic
│       ├── components/
│       │   ├── layout/                   # Stoic navigation, header & cards
│       │   ├── viewer/                   # PDF.js overlays & dual comparison
│       │   ├── findings/                 # Evidence-linked finding list & revisions
│       │   ├── financial/                # Reconciliation & running balance tables
│       │   ├── graph/                    # React Flow claim graph
│       │   ├── coverage/                 # Check applicability & outcome matrix
│       │   └── agent/                    # Reviewer copilot drawer
│       └── services/                     # Typed API client
│
├── ml/                                    # Machine Learning Training & Evaluation
│   ├── data_generation/                  # Fictional loan packet generator
│   ├── configs/                          # Hyperparameters & split definitions
│   ├── train.py                          # Torchvision MobileNetV3 Small trainer
│   ├── evaluate.py                       # Candidate recall & precision evaluator
│   ├── infer.py                          # Standalone inference adapter
│   └── colab_train.ipynb                 # Google Colab runnable training notebook
│
└── storage/                              # Local isolated file store
    ├── originals/                        # Read-only original uploads (SHA-256)
    ├── derivatives/                      # Rendered pages, evidence crops, previews
    ├── reports/                          # Generated immutable dossiers
    └── checkpoints/                      # Retained audit trail commitments
```

---

## 2. Dependency Compatibility & Smoke Test Plan

### Backend Dependencies (Python)
- Python target: `3.11` or `3.12` standard 64-bit Windows release.
- Core packages with pinned versions:
  - `fastapi==0.115.5`
  - `uvicorn[standard]==0.32.1`
  - `pydantic==2.10.2`
  - `sqlalchemy==2.0.36`
  - `alembic==1.14.0`
  - `pymupdf==1.25.0` (PyMuPDF / fitz for native text extraction)
  - `opencv-python-headless==4.10.0.84`
  - `pillow==11.0.0`
  - `torch==2.5.1+cpu`, `torchvision==0.20.1+cpu` (CPU baseline for fast local inference)
  - `reportlab==4.2.5` (PDF dossier rendering)
  - `pytest==8.3.4`, `pytest-asyncio==0.24.0`

### Frontend Dependencies (Node / npm)
- Verified Host: Node.js `v26.12.0`, npm `11.20.0`.
- Core packages with pinned versions:
  - `react==18.3.1`, `react-dom==18.3.1`
  - `vite==6.0.1`
  - `typescript==5.6.3`
  - `tailwindcss==3.4.15`, `autoprefixer==10.4.20`, `postcss==8.4.49`
  - `lucide-react==0.468.0` (minimalist line icons)
  - `pdfjs-dist==4.8.69` (PDF rendering & coordinate projection)
  - `@xyflow/react==12.3.5` (React Flow claim graph)

