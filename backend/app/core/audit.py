import json
import hashlib
from sqlalchemy.orm import Session
from backend.app.models.finding import AuditEvent

def canonical_json(data: dict) -> str:
    return json.dumps(data, sort_keys=True, separators=(',', ':'))

def compute_event_hash(prev_hash: str, seq: int, action_type: str, actor_id: str, payload_str: str) -> str:
    envelope = f"{prev_hash}|{seq}|{action_type}|{actor_id}|{payload_str}"
    return hashlib.sha256(envelope.encode('utf-8')).hexdigest()

def record_audit_event(
    db: Session,
    case_id: str,
    action_type: str,
    actor_id: str,
    payload: dict
) -> AuditEvent:
    # Fetch last event for case
    last_event = (
        db.query(AuditEvent)
        .filter(AuditEvent.case_id == case_id)
        .order_by(AuditEvent.sequence_number.desc())
        .first()
    )
    
    if last_event:
        seq = last_event.sequence_number + 1
        prev_hash = last_event.current_event_hash
    else:
        seq = 1
        prev_hash = "0" * 64  # Genesis hash
        
    payload_str = canonical_json(payload)
    curr_hash = compute_event_hash(prev_hash, seq, action_type, actor_id, payload_str)
    
    event = AuditEvent(
        case_id=case_id,
        sequence_number=seq,
        action_type=action_type,
        actor_id=actor_id,
        payload_json=payload_str,
        previous_event_hash=prev_hash,
        current_event_hash=curr_hash
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

def verify_case_audit_chain(db: Session, case_id: str) -> tuple[bool, str, int]:
    events = (
        db.query(AuditEvent)
        .filter(AuditEvent.case_id == case_id)
        .order_by(AuditEvent.sequence_number.asc())
        .all()
    )
    if not events:
        return True, "No events to verify", 0
        
    expected_prev = "0" * 64
    for idx, ev in enumerate(events, start=1):
        if ev.sequence_number != idx:
            return False, f"Broken sequence at event ID {ev.id}: expected {idx}, got {ev.sequence_number}", idx
        if ev.previous_event_hash != expected_prev:
            return False, f"Hash link mismatch at sequence {idx}: expected {expected_prev}, got {ev.previous_event_hash}", idx
        calculated = compute_event_hash(
            ev.previous_event_hash,
            ev.sequence_number,
            ev.action_type,
            ev.actor_id,
            ev.payload_json
        )
        if ev.current_event_hash != calculated:
            return False, f"Payload tampering detected at sequence {idx}: calculated {calculated}, got {ev.current_event_hash}", idx
        expected_prev = ev.current_event_hash
        
    return True, "Audit chain cryptographically valid", len(events)

