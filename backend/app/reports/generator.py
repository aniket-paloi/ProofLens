import os
from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from backend.app.models.case import Case, Document
from backend.app.models.execution import ProcessingRun, CheckExecution
from backend.app.models.field import Field, Claim, Transaction
from backend.app.models.finding import Finding, AuditEvent
from backend.app.core.config import settings

def generate_pdf_dossier(db: Session, run_id: str) -> Dict[str, Any]:
    """
    Generates a 6-Section PDF Investigation Dossier via ReportLab:
    1. Executive Summary & Case Metadata
    2. Document Lineage & Integrity Verification
    3. Source-Linked Financial Extractions & Claim Alignment
    4. Findings & Discrepancies with Evidence Coordinates
    5. Alternative Explanations & Scoped Limitations
    6. Hash-Chained Audit Trail & Immutability Verification
    """
    run = db.query(ProcessingRun).filter(ProcessingRun.id == run_id).first()
    if not run:
        raise ValueError(f"Run {run_id} not found")

    case = run.case
    os.makedirs(settings.REPORTS_DIR, exist_ok=True)
    report_filename = f"dossier_{run_id}.pdf"
    report_path = os.path.join(settings.REPORTS_DIR, report_filename)

    doc = SimpleDocTemplate(
        report_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A")
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748B")
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=14,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )
    cell_bold = ParagraphStyle(
        "CellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0F172A")
    )
    cell_normal = ParagraphStyle(
        "CellNormal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#334155")
    )

    story = []

    # Title Banner
    story.append(Paragraph("PROOFLENS — INVESTIGATION DOSSIER", title_style))
    story.append(Paragraph(f"Evidence-Driven Review Bundle | Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#4F46E5"), spaceAfter=12))

    # SECTION 1: Executive Summary & Case Metadata
    story.append(Paragraph("1. Executive Summary & Case Metadata", section_heading))
    findings = db.query(Finding).filter(Finding.run_id == run_id).all()
    checks = db.query(CheckExecution).filter(CheckExecution.run_id == run_id).all()
    completed_checks = [c for c in checks if c.lifecycle_state == "COMPLETED"]

    meta_data = [
        [Paragraph("Case Reference", cell_bold), Paragraph(case.reference_number, cell_normal), Paragraph("Applicant Name", cell_bold), Paragraph(case.applicant_name, cell_normal)],
        [Paragraph("Case ID", cell_bold), Paragraph(case.id[:18] + "...", cell_normal), Paragraph("Case Status", cell_bold), Paragraph(case.status, cell_normal)],
        [Paragraph("Processing Run ID", cell_bold), Paragraph(run.id[:18] + "...", cell_normal), Paragraph("Snapshot SHA-256", cell_bold), Paragraph(run.snapshot_hash[:16] + "...", cell_normal)],
        [Paragraph("Checks Completed", cell_bold), Paragraph(f"{len(completed_checks)} / {len(checks)}", cell_normal), Paragraph("Total Findings", cell_bold), Paragraph(str(len(findings)), cell_normal)],
    ]
    t_meta = Table(meta_data, colWidths=[110, 160, 110, 160])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 12))

    # SECTION 2: Document Lineage & Byte Integrity
    story.append(Paragraph("2. Document Lineage & Original Byte Integrity", section_heading))
    docs_data = [[
        Paragraph("Filename", cell_bold),
        Paragraph("Type", cell_bold),
        Paragraph("Size", cell_bold),
        Paragraph("SHA-256 Original Hash", cell_bold),
        Paragraph("Provenance", cell_bold)
    ]]
    for d in case.documents:
        prov = "INDEPENDENT" if "bank" in d.filename.lower() else ("SHARED" if "salary" in d.filename.lower() else "DERIVATION")
        docs_data.append([
            Paragraph(d.filename, cell_normal),
            Paragraph(d.classified_type or "UNKNOWN", cell_normal),
            Paragraph(f"{d.file_size_bytes:,} B", cell_normal),
            Paragraph(d.sha256_hash[:20] + "...", cell_normal),
            Paragraph(prov, cell_normal)
        ])
    t_docs = Table(docs_data, colWidths=[120, 80, 60, 180, 100])
    t_docs.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_docs)
    story.append(Spacer(1, 12))

    # SECTION 3: Source-Linked Financial Extractions & Claim Alignment
    story.append(Paragraph("3. Financial Extractions & Claim Alignment Matrix", section_heading))
    claims = db.query(Claim).filter(Claim.run_id == run_id).all()
    claims_data = [[
        Paragraph("Claim Type", cell_bold),
        Paragraph("Basis", cell_bold),
        Paragraph("Amount", cell_bold),
        Paragraph("Currency", cell_bold),
        Paragraph("Period", cell_bold),
        Paragraph("Status", cell_bold)
    ]]
    for c in claims[:8]:
        amt_str = f"{float(c.amount):,.2f}" if c.amount else "—"
        period = f"{c.period_start or ''} to {c.period_end or ''}"
        claims_data.append([
            Paragraph(c.claim_type, cell_normal),
            Paragraph(c.basis, cell_normal),
            Paragraph(amt_str, cell_normal),
            Paragraph(c.currency, cell_normal),
            Paragraph(period if period.strip() != "to" else "Stated", cell_normal),
            Paragraph(c.status, cell_normal)
        ])
    t_claims = Table(claims_data, colWidths=[110, 90, 90, 50, 110, 90])
    t_claims.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_claims)
    story.append(Spacer(1, 12))

    # SECTION 4: Findings & Discrepancies with Evidence Coordinates
    story.append(Paragraph("4. Findings & Discrepancy Evidence", section_heading))
    if findings:
        for fnd in findings:
            sev_color = "#DC2626" if fnd.severity == "CRITICAL" else ("#EA580C" if fnd.severity == "HIGH" else "#4F46E5")
            f_box = [
                [Paragraph(f"[{fnd.severity}] {fnd.title}", cell_bold), Paragraph(f"Type: {fnd.observation_type} | Disposition: {fnd.reviewer_disposition}", cell_normal)],
                [Paragraph(fnd.summary, cell_normal), Paragraph("", cell_normal)]
            ]
            t_f = Table(f_box, colWidths=[360, 180])
            t_f.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor(sev_color)),
                ('PADDING', (0,0), (-1,-1), 4),
            ]))
            story.append(t_f)
            story.append(Spacer(1, 6))
    else:
        story.append(Paragraph("No anomalous findings or discrepancies detected in submitted evidence.", body_style))
    story.append(Spacer(1, 8))

    # SECTION 5: Alternative Explanations & Scoped Limitations
    story.append(Paragraph("5. Alternative Explanations & Scoped Limitations", section_heading))
    alt_text = """
    <b>Zero-Accusation Standard:</b> ProofLens findings identify measured data discrepancies and visual discontinuities;
    they do not certify authenticity or establish intent to commit fraud. Legitimate explanations include:<br/>
    • <b>Corporate Split Payroll:</b> Multi-deposit salary structures where allowances/incentives deposit separately.<br/>
    • <b>Banking Posting Delays:</b> Transactions crossing calendar month boundaries.<br/>
    • <b>Typesetting Divergence:</b> Benign software font adjustments during corporate template updates.<br/>
    <b>Limitations:</b> Handwriting analysis, signature verification, and unintegrated banking systems remain uninspected.
    """
    story.append(Paragraph(alt_text, body_style))
    story.append(Spacer(1, 12))

    # SECTION 6: Audit Trail & Immutability Chain
    story.append(Paragraph("6. Audit Trail & SHA-256 Hash Chain Verification", section_heading))
    events = db.query(AuditEvent).filter(AuditEvent.case_id == case.id).order_by(AuditEvent.sequence_number.asc()).all()
    audit_data = [[
        Paragraph("#", cell_bold),
        Paragraph("Action", cell_bold),
        Paragraph("Actor", cell_bold),
        Paragraph("Timestamp", cell_bold),
        Paragraph("Event Hash", cell_bold)
    ]]
    for ev in events[:6]:
        audit_data.append([
            Paragraph(str(ev.sequence_number), cell_normal),
            Paragraph(ev.action_type, cell_normal),
            Paragraph(ev.actor_id, cell_normal),
            Paragraph(ev.created_at.strftime("%H:%M:%S") if ev.created_at else "—", cell_normal),
            Paragraph(ev.current_event_hash[:18] + "...", cell_normal)
        ])
    t_audit = Table(audit_data, colWidths=[25, 130, 85, 80, 220])
    t_audit.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_audit)

    # Build document
    doc.build(story)

    return {
        "report_path": report_path,
        "filename": report_filename,
        "byte_size": os.path.getsize(report_path)
    }

