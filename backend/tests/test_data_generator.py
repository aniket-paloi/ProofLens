import os
import json
import pytest
import pymupdf
from backend.generator.generate_packets import get_12_curated_packet_definitions, generate_all_packets_and_manifests

def test_curated_packet_definitions():
    cases = get_12_curated_packet_definitions()
    assert len(cases) == 12

    train_cases = [c for c in cases if c.split.value == "TRAIN"]
    val_cases = [c for c in cases if c.split.value == "VAL"]
    test_cases = [c for c in cases if c.split.value == "TEST"]

    assert len(train_cases) == 6
    assert len(val_cases) == 2
    assert len(test_cases) == 4

    # Verify reference numbers are unique
    refs = [c.reference_number for c in cases]
    assert len(refs) == len(set(refs))

def test_manifest_and_packet_generation(tmp_path):
    summary = generate_all_packets_and_manifests(output_dir=str(tmp_path))
    assert summary["total_cases"] == 12
    assert summary["train_count"] == 6
    assert summary["val_count"] == 2
    assert summary["test_count"] == 4

    manifests_dir = os.path.join(tmp_path, "manifests")
    packets_dir = os.path.join(tmp_path, "fictional_packets")

    # Load manifests
    with open(os.path.join(manifests_dir, "train_manifest.json")) as f:
        train = json.load(f)
    with open(os.path.join(manifests_dir, "val_manifest.json")) as f:
        val = json.load(f)
    with open(os.path.join(manifests_dir, "test_manifest.json")) as f:
        test = json.load(f)
    with open(os.path.join(manifests_dir, "ground_truth.json")) as f:
        gt = json.load(f)

    # Invariant: Disjoint splits
    train_refs = set(c["reference_number"] for c in train)
    val_refs = set(c["reference_number"] for c in val)
    test_refs = set(c["reference_number"] for c in test)

    assert len(train_refs.intersection(val_refs)) == 0, "Train and Val must be disjoint"
    assert len(train_refs.intersection(test_refs)) == 0, "Train and Test must be disjoint"
    assert len(val_refs.intersection(test_refs)) == 0, "Val and Test must be disjoint"
    assert len(train_refs | val_refs | test_refs) == 12

    # Verify ground truth contains all 12
    assert len(gt) == 12
    for ref in train_refs | val_refs | test_refs:
        assert ref in gt

    # Verify physical PDF files for each packet
    required_files = [
        "application_form.pdf",
        "salary_slip_m1.pdf",
        "salary_slip_m2.pdf",
        "salary_slip_m3.pdf",
        "bank_statement_3mo.pdf"
    ]

    for ref in train_refs | val_refs | test_refs:
        case_dir = os.path.join(packets_dir, ref)
        assert os.path.isdir(case_dir)
        for req in required_files:
            file_path = os.path.join(case_dir, req)
            assert os.path.exists(file_path), f"Missing {req} in {ref}"
            assert os.path.getsize(file_path) > 500, f"File {req} in {ref} too small"

            # Verify PDF is valid and readable by PyMuPDF
            doc = pymupdf.open(file_path)
            assert doc.page_count >= 1
            doc.close()

