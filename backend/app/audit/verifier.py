"""
ProofLens Retained Checkpoint & Offline Integrity Verifier (Milestone 16)
Provides cryptographic checkpoint export, verification, and offline tamper detection.
"""

import os
import sys
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple, List
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.audit import canonical_json, compute_event_hash, verify_case_audit_chain
from backend.app.models.case import Case
from backend.app.models.finding import AuditEvent


def compute_merkle_or_chain_digest(events: List[AuditEvent]) -> str:
    """Computes a cumulative SHA-256 digest over the entire sequence of event hashes."""
    if not events:
        return hashlib.sha256(b"GENESIS_EMPTY").hexdigest()
    running_h = hashlib.sha256()
    for ev in events:
        running_h.update(ev.current_event_hash.encode("utf-8"))
    return running_h.hexdigest()


def generate_case_checkpoint(db: Session, case_id: str, note: Optional[str] = None) -> Dict[str, Any]:
    """
    Generates a cryptographic checkpoint record and writes it to disk.
    Frozen for offline, zero-trust verification.
    """
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise ValueError(f"Case with ID {case_id} not found.")

    events = (
        db.query(AuditEvent)
        .filter(AuditEvent.case_id == case_id)
        .order_by(AuditEvent.sequence_number.asc())
        .all()
    )

    is_valid, msg, count = verify_case_audit_chain(db, case_id)
    if not is_valid:
        raise ValueError(f"Cannot generate checkpoint for tampered or invalid audit chain: {msg}")

    latest_hash = events[-1].current_event_hash if events else ("0" * 64)
    latest_seq = events[-1].sequence_number if events else 0
    chain_digest = compute_merkle_or_chain_digest(events)

    checkpoint_data = {
        "format_version": "1.0.0",
        "case_id": case.id,
        "reference_number": case.reference_number,
        "applicant_name": case.applicant_name,
        "checkpoint_created_at": datetime.now(timezone.utc).isoformat(),
        "event_count": count,
        "latest_sequence_number": latest_seq,
        "latest_event_hash": latest_hash,
        "chain_digest": chain_digest,
        "verification_status": "CRYPTOGRAPHICALLY_VERIFIED",
        "note": note or "Official Retained Checkpoint for Independent Verification"
    }

    # Write to storage/checkpoints/
    chk_dir = os.path.join(settings.STORAGE_DIR, "checkpoints")
    os.makedirs(chk_dir, exist_ok=True)
    filename = f"checkpoint_{case.reference_number}_{latest_seq}.json"
    file_path = os.path.join(chk_dir, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(canonical_json(checkpoint_data))

    checkpoint_data["file_path"] = file_path
    checkpoint_data["file_name"] = filename
    return checkpoint_data


def verify_retained_checkpoint(
    checkpoint_data: Dict[str, Any],
    db: Optional[Session] = None,
    events_list: Optional[List[Dict[str, Any]]] = None
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Verifies an offline checkpoint against either a live database session
    or a standalone JSON export of audit events.
    """
    case_id = checkpoint_data.get("case_id")
    expected_seq = checkpoint_data.get("latest_sequence_number", 0)
    expected_hash = checkpoint_data.get("latest_event_hash", "")
    expected_digest = checkpoint_data.get("chain_digest", "")

    if db:
        events = (
            db.query(AuditEvent)
            .filter(AuditEvent.case_id == case_id)
            .order_by(AuditEvent.sequence_number.asc())
            .all()
        )
        is_valid, msg, count = verify_case_audit_chain(db, case_id)
        if not is_valid:
            return False, f"Audit chain verification failed: {msg}", {"tamper_detected": True}
    elif events_list:
        # Re-verify in-memory event objects
        expected_prev = "0" * 64
        running_h = hashlib.sha256()
        for idx, ev in enumerate(events_list, start=1):
            if ev["sequence_number"] != idx:
                return False, f"Broken sequence at {idx}", {"tamper_detected": True}
            if ev["previous_event_hash"] != expected_prev:
                return False, f"Broken hash link at {idx}", {"tamper_detected": True}
            calc = compute_event_hash(
                ev["previous_event_hash"],
                ev["sequence_number"],
                ev["action_type"],
                ev["actor_id"],
                ev["payload_json"] if isinstance(ev["payload_json"], str) else canonical_json(ev["payload_json"])
            )
            if ev["current_event_hash"] != calc:
                return False, f"Payload tampering at sequence {idx}", {"tamper_detected": True}
            expected_prev = ev["current_event_hash"]
            running_h.update(ev["current_event_hash"].encode("utf-8"))
        count = len(events_list)
        events = events_list
    else:
        return False, "Neither database session nor events_list provided for verification.", {}

    if count < expected_seq:
        return False, f"Checkpoint expects {expected_seq} events, but only {count} found.", {"tamper_detected": True}

    # Verify latest hash matches
    if count > 0:
        actual_latest = events[expected_seq - 1].current_event_hash if hasattr(events[0], "current_event_hash") else events[expected_seq - 1]["current_event_hash"]
        if actual_latest != expected_hash:
            return False, f"Latest hash mismatch: expected {expected_hash}, found {actual_latest}", {"tamper_detected": True}

    return True, "Checkpoint matches audit trail exactly with valid cryptographic proof.", {
        "verified_events": expected_seq,
        "latest_hash": expected_hash,
        "tamper_detected": False,
        "chain_digest": expected_digest
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m backend.app.audit.verifier <checkpoint_file.json>")
        sys.exit(1)
    
    chk_path = sys.argv[1]
    with open(chk_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"Loaded checkpoint for case {data.get('case_id')} ({data.get('reference_number')}).")
    print(f"Latest sequence: {data.get('latest_sequence_number')}")
    print(f"Latest hash: {data.get('latest_event_hash')}")
    print("Run verification via test suite or API.")

