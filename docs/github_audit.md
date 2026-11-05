# ProofLens Research Repository Audit (Milestone 01)

**Audit Date:** 5 November 2026  
**Auditor:** ProofLens Architecture Team  
**Scope:** 9 research and open-source references listed in `ProofLens_Antigravity_Prompt_Pack.md`.

---

## 1. Repository Findings Matrix

| Repository | Focus / Domain | Key Components Inspected | Extraction & Geometry Handling | Licenses / Reuse Decision | Key Takeaway / Why Not Direct Import |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Doc-Verify** (`Ojas2095/doc-verify`) | Flask + Tesseract + Ollama/Local LLM heuristic verification | `app.py`, basic extraction routes | Discards token coordinates; aggregates OCR text into flat strings. | MIT License. **Decision:** Do not import. Discarding coordinates violates our core invariant (source evidence linking). |
| **Document-Forensics** (`MukeshK17/document-forensics`) | PAN-card verification with patch CNN & OCR | Traditional CV filters (Laplacian, ELA) + OCR | Pan-card specific bounding boxes; not generalized to tabular salary slips or bank statements. | Custom / unspecified. **Decision:** Do not import. Adapt only explainable sharpness & contrast variance equations in pure Python/OpenCV. |
| **DocGuard-VLM** (`kratos0718/docguard-vlm`) | Qwen2-VL fine-tuned adapter for forgery classification | VLM prompt harness, evaluation scripts | Bounding boxes hallucinated or loose text spans; lacks pixel-level certainty. | Apache 2.0. **Decision:** Reference for evaluation protocols only. VLM reasoning cannot be treated as forensic proof. |
| **Document-Fraud-Detection** (`vignesh865/document-fraud-detection`) | Traditional CV + Gemini API heuristics | Notebooks & scripts | Several visual strategies marked "pending" or unexecuted. | Unlicensed/MIT. **Decision:** Do not import. Avoid exploratory code that promises unverified detectors. |
| **CrossVerify** (`kanija16/CrossVerify`) | Multi-modal identity document fusion & leakage control | Grouped cross-validation splits, late fusion | Identity-card oriented; lacks multi-page financial reconciliation logic. | Academic use only. **Decision:** Adopt group-aware cross-validation split methodology (disjoint template/applicant groups) in our data generator. |
| **ARGUS** (`mittalpk/ARGUS`) | Document forgery classifier packaging | Torch vision scripts & inference server | Patch-level classification; claims 99% production accuracy on closed ID dataset. | MIT. **Decision:** Replicate clean model packaging and model card discipline; do not rely on unverified accuracy claims. |
| **DocTamper** (`qcf-568/DocTamper`) | CVPR 2023 text tampering localization | Segmentation model architectures | Full-page segmentation masks; requires extensive GPU compute and heavy weights. | Research only / Non-commercial dataset terms. **Decision:** Defer to optional Prompt 19. Not suitable for lightweight CPU core. |
| **ForensicHub** (`scu-zjz/ForensicHub`) | Modular benchmark framework for image manipulation | Multi-model benchmark suite | General image manipulation (splicing, copy-move), not financial document text semantics. | Mixed licenses across sub-modules. **Decision:** Reference for evaluation metrics (IoU, F1). Not a drop-in loan investigation backend. |
| **RTM** (`DrLuo/RTM`) | Robust Text Manipulation detection | Text detection + manipulation heads | Tampered test examples were used for parameter tuning in source repo. | Apache 2.0 / Academic. **Decision:** Reference only. Avoid evaluation data leakage; maintain strictly untouched test sets. |

---

## 2. Minimal Integration Plan & Recommendation

Instead of merging disparate, poorly maintained, or incompatible third-party repositories:
1. **Fresh Modular Build:** Build the core application from scratch using mature, industry-standard, permissively licensed libraries (`FastAPI`, `SQLAlchemy`, `PyMuPDF`, `OpenCV`, `Torchvision`, `ReportLab`, `React`, `Tailwind`).
2. **Deterministic Geometry & Coordinate Invariants:** Preserve normalized `[ymin, xmin, ymax, xmax]` in `[0,1]` relative to original page dimensions and rotation angles.
3. **Financial Intelligence:** Implement Python `Decimal` arithmetic directly for salary credit matching, period alignment, and running balances.
4. **Lightweight Visual Baseline:** Implement OpenCV-based text sharpness, background variance, and font baseline heuristics, combined with a Torchvision MobileNetV3 Small region classifier.

