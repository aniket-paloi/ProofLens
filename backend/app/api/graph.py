from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.models.case import Case, Document, Page
from backend.app.models.field import Field, Claim, Transaction
from backend.app.models.finding import Finding, EvidenceLink
from backend.app.models.execution import ProcessingRun, VisualObservation

def build_case_claim_graph(db: Session, run_id: str) -> Dict[str, Any]:
    """
    Constructs a read projection claim and source-dependency graph:
    Nodes: Documents, Pages, Fields, Claims, Transactions, Observations, Findings.
    Edges: Typed source connections with explicit provenance semantics.
    """
    run = db.query(ProcessingRun).filter(ProcessingRun.id == run_id).first()
    if not run:
        return {"nodes": [], "edges": [], "provenance_summary": {}}

    case = run.case
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []

    # 1. Document Nodes
    for doc in case.documents:
        doc_lower = doc.filename.lower()
        if "bank" in doc_lower or "statement" in doc_lower:
            prov = "INDEPENDENT_ACQUISITION"
        elif "salary" in doc_lower or "slip" in doc_lower:
            prov = "POSSIBLE_SHARED_SOURCE"
        else:
            prov = "KNOWN_DERIVATION"

        nodes.append({
            "id": f"doc_{doc.id}",
            "type": "DOCUMENT",
            "label": doc.filename,
            "provenance": prov,
            "data": {
                "document_id": doc.id,
                "mime_type": doc.mime_type,
                "sha256": doc.sha256_hash[:12] + "..."
            }
        })

        # 2. Page Nodes
        for page in doc.pages:
            p_node_id = f"page_{page.id}"
            nodes.append({
                "id": p_node_id,
                "type": "PAGE",
                "label": f"{doc.filename} (p. {page.page_number})",
                "data": {
                    "page_id": page.id,
                    "page_number": page.page_number,
                    "has_native_text": bool(page.has_native_text)
                }
            })
            edges.append({
                "id": f"e_doc_page_{page.id}",
                "source": f"doc_{doc.id}",
                "target": p_node_id,
                "type": "CONTAINS"
            })

    # 3. Field Nodes
    fields = db.query(Field).filter(Field.run_id == run_id).all()
    for fld in fields:
        f_node_id = f"field_{fld.id}"
        nodes.append({
            "id": f_node_id,
            "type": "FIELD",
            "label": f"{fld.field_name}: {fld.raw_value}",
            "data": {
                "field_name": fld.field_name,
                "value": fld.normalized_value or fld.raw_value,
                "numeric_value": float(fld.numeric_value) if fld.numeric_value else None,
                "revision": fld.current_revision_num
            }
        })
        if fld.page_id:
            edges.append({
                "id": f"e_page_fld_{fld.id}",
                "source": f"page_{fld.page_id}",
                "target": f_node_id,
                "type": "EXTRACTED_FROM"
            })

    # 4. Claim Nodes
    claims = db.query(Claim).filter(Claim.run_id == run_id).all()
    for clm in claims:
        c_node_id = f"claim_{clm.id}"
        nodes.append({
            "id": c_node_id,
            "type": "CLAIM",
            "label": f"{clm.claim_type} ({clm.basis}): {float(clm.amount):,.2f} INR" if clm.amount else clm.claim_type,
            "data": {
                "basis": clm.basis,
                "amount": float(clm.amount) if clm.amount else None,
                "status": clm.status
            }
        })
        # Link from supporting fields
        for fld_id in (clm.supporting_field_ids or []):
            edges.append({
                "id": f"e_fld_clm_{fld_id}_{clm.id}",
                "source": f"field_{fld_id}",
                "target": c_node_id,
                "type": "SUPPORTS"
            })

    # 5. Transaction Nodes
    txs = db.query(Transaction).filter(Transaction.run_id == run_id).all()
    for tx in txs:
        t_node_id = f"tx_{tx.id}"
        nodes.append({
            "id": t_node_id,
            "type": "TRANSACTION",
            "label": f"{tx.transaction_date} [{tx.transaction_type}] {float(tx.amount):,.2f} INR",
            "data": {
                "date": tx.transaction_date,
                "narration": tx.narration,
                "type": tx.transaction_type,
                "amount": float(tx.amount)
            }
        })
        if tx.page_id:
            edges.append({
                "id": f"e_page_tx_{tx.id}",
                "source": f"page_{tx.page_id}",
                "target": t_node_id,
                "type": "RECORDED_ON"
            })

    # 6. Finding Nodes
    findings = db.query(Finding).filter(Finding.run_id == run_id).all()
    for fnd in findings:
        fn_node_id = f"finding_{fnd.id}"
        nodes.append({
            "id": fn_node_id,
            "type": "FINDING",
            "label": f"[{fnd.severity}] {fnd.title}",
            "data": {
                "severity": fnd.severity,
                "type": fnd.observation_type,
                "disposition": fnd.reviewer_disposition
            }
        })
        for link in fnd.evidence_links:
            target_prefix = link.entity_type.lower()
            edges.append({
                "id": f"e_fnd_link_{link.id}",
                "source": fn_node_id,
                "target": f"{target_prefix}_{link.entity_id}",
                "type": "EVIDENCE_FOR",
                "role": link.role
            })

    return {
        "run_id": run_id,
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "nodes": nodes,
        "edges": edges,
        "provenance_summary": {
            "known_derivation_count": sum(1 for n in nodes if n.get("provenance") == "KNOWN_DERIVATION"),
            "possible_shared_source_count": sum(1 for n in nodes if n.get("provenance") == "POSSIBLE_SHARED_SOURCE"),
            "independent_acquisition_count": sum(1 for n in nodes if n.get("provenance") == "INDEPENDENT_ACQUISITION"),
            "invariant_note": "Agreeing values between application and payslips share corporate/applicant provenance and do NOT constitute independent confirmation."
        }
    }

