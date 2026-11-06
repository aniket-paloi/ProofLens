# ProofLens Packaging & Distribution Manifest (Milestone 18)

**Package Version:** 0.2.0-enterprise  
**Release Date:** 6 November 2026  
**Target Environment:** Local Standalone Windows 11 / Linux AMD64  

---

## 1. System Inventory & Offline Assets

| Component | Path | Description | Checksum / Size |
| :--- | :--- | :--- | :--- |
| **FastAPI Backend** | `backend/app/` | Asynchronous REST API, SQLite WAL persistence, deterministic engines | Core code |
| **Persistent Local Worker** | `backend/worker/` | Multi-stage pipeline runner with retry idempotency | Core worker |
| **React/Vite Frontend** | `frontend/` | 3-panel workspace, dual crop inspector, reconciliation tree | Built in `frontend/dist` |
| **Region Classifier Model** | `ml/checkpoints/mobilenet_v3_small_region.pt` | Trained MobileNetV3 Small binary region manipulator detector | 6.2 MB (TorchScript/PT) |
| **Model Card** | `ml/MODEL_CARD.md` | Training metrics, intended use, and limitations | Documentation |
| **Fictional Datasets** | `data/fictional_packets/` | 12 curated multi-document loan application packets | 12 complete dossiers |
| **Split Manifests** | `data/manifests/` | Disjoint `train_manifest.json`, `val_manifest.json`, `test_manifest.json` | JSON manifests |
| **One-Click Launchers** | `start_prooflens.ps1` & `run_prooflens.bat` | Dual server startup scripts for PowerShell and CMD | Automation |

---

## 2. Hardware & Runtime Prerequisites
- **Operating System:** Windows 10/11 or Ubuntu 22.04 LTS (AMD64)
- **Node.js:** v20+ (Verified on Node v26.12.0 / npm 11.20.0)
- **Python:** Python 3.11 – 3.13 (PyTorch CPU, OpenCV, PyMuPDF, ReportLab)
- **Storage:** Minimum 1 GB free disk space for document rendering derivatives

---

## 3. Quick Startup Instructions

### Option A: PowerShell Launcher
```powershell
.\start_prooflens.ps1
```

### Option B: Batch / CMD Launcher
```cmd
run_prooflens.bat
```

### Option C: Manual Terminal Launch
1. **Terminal 1 (Backend):**
   ```bash
   python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
2. **Terminal 2 (Frontend):**
   ```bash
   cd frontend
   npm run dev -- --host 127.0.0.1 --port 5173
   ```
3. Open browser at [http://127.0.0.1:5173/](http://127.0.0.1:5173/)

---

## 4. Test Suite Execution
To verify all 22 milestones and system integrity:
```bash
python -m pytest backend/tests/ -v
```
To run the blind test evaluation benchmark:
```bash
python -c "from backend.evaluation.eval_suite import run_blind_evaluation; print(run_blind_evaluation())"
```

