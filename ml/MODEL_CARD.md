# ProofLens Region Classifier Model Card

## Model Overview
- **Model Architecture:** MobileNetV3 Small (Torchvision) with single logit linear output head.
- **Task:** Binary candidate crop manipulation scoring (0 = Authentic, 1 = Manipulated / Spliced).
- **Target Resolution:** 224 x 224 RGB, ImageNet normalization.

## Dataset & Training Splits
- **Training Split:** 6 disjoint fictional loan packets (`LOAN-2026-TR01` through `LOAN-2026-TR06`).
- **Validation Split:** 2 disjoint fictional loan packets (`LOAN-2026-VA01`, `LOAN-2026-VA02`).
- **Test Split:** 4 disjoint held-out fictional loan packets (`LOAN-2026-TE01` through `LOAN-2026-TE04`) withheld from training.

## Performance Metrics & Honest Capabilities
- **Inference Latency:** ~25ms on CPU per crop.
- **Decision Threshold:** 0.50 manipulation probability.
- **Limitations:** Trained on clean and perturbed synthetic loan documents; not guaranteed on unconstrained scanned handwriting or photographic noise. Outputs represent local manipulation probability, never absolute legal fraud determination.
