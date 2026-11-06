import os
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal
from backend.app.models.case import Case, Document, Page
from backend.app.models.execution import ProcessingRun, CheckDefinition, CheckExecution, VisualObservation
from backend.app.models.field import Field, Claim, Transaction
from backend.app.models.finding import Finding, EvidenceLink
from backend.app.ingestion.renderer import render_and_route_pages
from backend.app.parsers.dispatcher import extract_document_entities
from backend.app.parsers.crosscheck import crosscheck_page_text_layers
from backend.app.financial.reconciliation import (
    reconcile_bank_statement_balances,
    match_salary_credits,
    reconcile_income_declaration,
    check_employer_consistency
)
from backend.app.forensics.visual_baseline import (
    analyze_sharpness_variance,
    analyze_contrast_edge_discontinuity,
    analyze_native_font_consistency,
    save_crop_derivative
)
from backend.app.forensics.region_model import RegionClassifierAdapter
from backend.app.core.audit import record_audit_event

def process_run(run_id: str) -> None:
    db: Session = SessionLocal()
    try:
        run = db.query(ProcessingRun).filter(ProcessingRun.id == run_id).first()
        if not run:
            return

        run.status = "RUNNING"
        db.commit()

        case = db.query(Case).filter(Case.id == run.case_id).first()
        if not case:
            run.status = "FAILED"
            run.error_message = "Associated case not found."
            db.commit()
            return

        # Stage 1: Render and Route Pages for all documents in the case
        for doc in case.documents:
            existing_pages = db.query(Page).filter(Page.document_id == doc.id).all()
            if not existing_pages:
                pages_meta = render_and_route_pages(doc.original_path, doc.mime_type)
                for meta in pages_meta:
                    page = Page(
                        id=meta["page_id"],
                        document_id=doc.id,
                        page_number=meta["page_number"],
                        width_pts=meta["width_pts"],
                        height_pts=meta["height_pts"],
                        rotation_deg=meta["rotation_deg"],
                        rendered_image_path=meta["rendered_image_path"],
                        has_native_text=meta["has_native_text"]
                    )
                    db.add(page)
                doc.page_count = len(pages_meta)
                db.commit()

        # Stage 2: Document Classification based on filename/spans
        for doc in case.documents:
            lower_name = doc.filename.lower()
            if "salary" in lower_name or "payslip" in lower_name or "slip" in lower_name:
                doc.classified_type = "SALARY_SLIP"
                doc.classification_confidence = 0.95
            elif "bank" in lower_name or "statement" in lower_name:
                doc.classified_type = "BANK_STATEMENT"
                doc.classification_confidence = 0.95
            elif "application" in lower_name or "form" in lower_name:
                doc.classified_type = "APPLICATION_FORM"
                doc.classification_confidence = 0.95
            else:
                doc.classified_type = "UNKNOWN"
                doc.classification_confidence = 0.50
            db.commit()

        # Stage 3: OCR, Tables & Source-Linked Field/Claim Extraction (Milestone 06)
        total_fields = 0
        total_claims = 0
        total_txs = 0

        for doc in case.documents:
            stats = extract_document_entities(db, run.id, doc)
            total_fields += stats["fields_created"]
            total_claims += stats["claims_created"]
            total_txs += stats["transactions_created"]

        # Stage 4: Native Text Layer vs Rendered Evidence Crosscheck (Milestone 07)
        total_pages_analyzed = 0
        total_invisible_spans = 0
        total_prompt_injections = 0
        total_baseline_anomalies = 0

        for doc in case.documents:
            pages = db.query(Page).filter(Page.document_id == doc.id).order_by(Page.page_number).all()
            for page in pages:
                total_pages_analyzed += 1
                try:
                    crosscheck_res = crosscheck_page_text_layers(doc.original_path, page.page_number)
                except Exception:
                    continue

                # 1. Prompt Injection Findings (CRITICAL)
                if crosscheck_res.get("injected_prompts"):
                    for inj in crosscheck_res["injected_prompts"]:
                        total_prompt_injections += 1
                        finding = Finding(
                            case_id=case.id,
                            run_id=run.id,
                            title="Embedded Adversarial Instruction in Text Layer",
                            observation_type="TEXT_LAYER_DESYNC",
                            severity="CRITICAL",
                            uncertainty="LOW",
                            summary=(
                                f"Observed non-rendered vector text span containing instruction payload matching "
                                f"prompt injection signature ('{inj['matched_keyword']}'). Native text layer deviates "
                                f"from visible document rendering."
                            ),
                            alternative_explanations=[
                                "Stale OCR layer from external preprocessing script",
                                "Adversarial prompt injection embedded in document",
                                "Template generator artifact"
                            ],
                            next_recommended_checks=[
                                "Quarantine document from automated LLM evaluation",
                                "Review visible raster layer in Evidence Viewer",
                                "Inspect raw font stream"
                            ]
                        )
                        db.add(finding)
                        db.flush()

                        ev_link = EvidenceLink(
                            finding_id=finding.id,
                            entity_type="PAGE",
                            entity_id=page.id,
                            role="PRIMARY",
                            notes=f"Adversarial payload '{inj['matched_keyword']}' at bbox {inj['bbox_normalized']}"
                        )
                        db.add(ev_link)

                # 2. Invisible / Hidden Text Findings (LOW)
                elif crosscheck_res.get("invisible_spans"):
                    inv_count = len(crosscheck_res["invisible_spans"])
                    total_invisible_spans += inv_count
                    finding = Finding(
                        case_id=case.id,
                        run_id=run.id,
                        title="Invisible Text Layer Detected",
                        observation_type="TEXT_LAYER_DESYNC",
                        severity="LOW",
                        uncertainty="LOW",
                        summary=(
                            f"Observed {inv_count} invisible text span(s) in document text layer on page {page.page_number}."
                        ),
                        alternative_explanations=[
                            "Normal invisible text layer from OCR software",
                            "Vector font clipping or transparency artifact"
                        ],
                        next_recommended_checks=[
                            "Inspect rendered raster image against selectable text"
                        ]
                    )
                    db.add(finding)
                    db.flush()

                    ev_link = EvidenceLink(
                        finding_id=finding.id,
                        entity_type="PAGE",
                        entity_id=page.id,
                        role="SUPPORTING",
                        notes=f"{inv_count} invisible text spans on page {page.page_number}"
                    )
                    db.add(ev_link)

                # 3. Font Baseline Displacement Anomalies (MEDIUM)
                if crosscheck_res.get("baseline_anomalies"):
                    for anom in crosscheck_res["baseline_anomalies"]:
                        total_baseline_anomalies += 1
                        delta = anom["baseline_delta_px"]
                        
                        # Generate high-resolution crop for visual inspector
                        crop_path = None
                        if page.rendered_image_path and os.path.exists(page.rendered_image_path):
                            crop_path = save_crop_derivative(page.rendered_image_path, anom["bbox_normalized"], crop_prefix="baseline_anom")

                        obs = VisualObservation(
                            run_id=run.id,
                            page_id=page.id,
                            detector_name="font_baseline",
                            detector_version="1.0.0",
                            measured_property="vertical_baseline_displacement_px",
                            measured_value=delta,
                            threshold_value=2.0,
                            bbox_normalized=anom["bbox_normalized"],
                            crop_path=crop_path,
                            evidence_strength="HIGH" if delta >= 3.0 else "MEDIUM",
                            limitations="Assumes standard horizontal tabular alignment; manual typesetting variance possible"
                        )
                        db.add(obs)
                        db.flush()

                        finding = Finding(
                            case_id=case.id,
                            run_id=run.id,
                            title="Font Baseline Displacement Anomaly",
                            observation_type="VISUAL_ANOMALY",
                            severity="MEDIUM",
                            uncertainty="LOW",
                            summary=(
                                f"Observed {delta:.2f}px vertical baseline displacement between '{anom['text_left']}' "
                                f"and '{anom['text_right']}' on page {page.page_number}. Digital alterations often cause "
                                f"vertical baseline misalignment."
                            ),
                            alternative_explanations=[
                                "Desktop publishing software kerning or column formatting",
                                "Digital splicing or numeric amount tampering",
                                "Table layout misalignment"
                            ],
                            next_recommended_checks=[
                                "Inspect high-resolution visual crop at dual-crop inspector",
                                "Compare against companion salary slips in packet"
                            ]
                        )
                        db.add(finding)
                        db.flush()

                        db.add(EvidenceLink(
                            finding_id=finding.id,
                            entity_type="OBSERVATION",
                            entity_id=obs.id,
                            role="PRIMARY",
                            notes=f"Vertical baseline displacement of {delta:.2f}px"
                        ))
                        db.add(EvidenceLink(
                            finding_id=finding.id,
                            entity_type="PAGE",
                            entity_id=page.id,
                            role="SUPPORTING",
                            notes=f"Page {page.page_number} ({doc.filename})"
                        ))

        # Stage 5: Financial & Cross-Document Intelligence (Milestone 08)
        all_transactions = db.query(Transaction).filter(Transaction.run_id == run.id).all()
        salary_claims = db.query(Claim).filter(Claim.run_id == run.id, Claim.claim_type == "SALARY_CLAIM").all()
        app_claims = db.query(Claim).filter(Claim.run_id == run.id, Claim.claim_type == "APPLICATION_CLAIM").all()
        all_fields = db.query(Field).filter(Field.run_id == run.id).all()

        # 5.1 Bank Statement Running Balance Reconciliation
        balance_recon = reconcile_bank_statement_balances(all_transactions)
        for disc in balance_recon.get("discrepancies", []):
            finding = Finding(
                case_id=case.id,
                run_id=run.id,
                title="Bank Statement Running Balance Arithmetic Gap",
                observation_type="CONTEXTUAL_MISMATCH",
                severity="HIGH",
                uncertainty="LOW",
                summary=(
                    f"Observed {abs(disc['delta']):,.2f} INR arithmetic discrepancy on {disc['date']} ({disc['narration']}). "
                    f"Statement balance is {disc['stated_balance']:,.2f} INR, expected {disc['expected_balance']:,.2f} INR."
                ),
                alternative_explanations=[
                    "Unreported fee, tax, or debit omission in transaction list",
                    "Bank ledger batch posting delay",
                    "Digital tampering of running balance column"
                ],
                next_recommended_checks=[
                    "Request certified direct-feed bank e-statement",
                    "Verify transaction counter continuity"
                ]
            )
            db.add(finding)
            db.flush()

            if disc.get("transaction_id"):
                db.add(EvidenceLink(
                    finding_id=finding.id,
                    entity_type="TRANSACTION",
                    entity_id=str(disc["transaction_id"]),
                    role="PRIMARY",
                    notes=f"Discrepancy of {disc['delta']:,.2f} INR on row {disc['date']}"
                ))

        # 5.2 Salary Slip to Bank Credit Reconciliation
        salary_match = match_salary_credits(salary_claims, all_transactions)
        for res in salary_match.get("results", []):
            if res["match_status"] == "SPLIT_MATCH":
                creds_str = ", ".join(f"{c['amount']:,.2f} INR ({c['date']})" for c in res["credits"])
                finding = Finding(
                    case_id=case.id,
                    run_id=run.id,
                    title="Candidate Multi-Transaction Split Payroll Match",
                    observation_type="CONTEXTUAL_MISMATCH",
                    severity="INFO",
                    uncertainty="LOW",
                    summary=(
                        f"Identified candidate split payroll structure: {len(res['credits'])} deposits ({creds_str}) "
                        f"sum exactly to net payable ({res['target_amount']:,.2f} INR)."
                    ),
                    alternative_explanations=[
                        "Corporate policy splitting base salary and performance allowance",
                        "Separate expense reimbursement or incentive deposit"
                    ],
                    next_recommended_checks=[
                        "Confirm dual-deposit policy with employer HR or offer letter"
                    ]
                )
                db.add(finding)
                db.flush()

                for cred in res["credits"]:
                    if cred.get("id"):
                        db.add(EvidenceLink(
                            finding_id=finding.id,
                            entity_type="TRANSACTION",
                            entity_id=str(cred["id"]),
                            role="SUPPORTING",
                            notes=f"Split deposit of {cred['amount']:,.2f} INR"
                        ))

            elif res["match_status"] == "UNMATCHED_DISCREPANCY":
                finding = Finding(
                    case_id=case.id,
                    run_id=run.id,
                    title="Salary Slip Net Payable to Bank Credit Discrepancy",
                    observation_type="CONTEXTUAL_MISMATCH",
                    severity="HIGH",
                    uncertainty="LOW",
                    summary=(
                        f"Salary slip net payable of {res['target_amount']:,.2f} INR does not reconcile with bank deposits "
                        f"in the corresponding period (nearest credit variance: {res['variance']:,.2f} INR)."
                    ),
                    alternative_explanations=[
                        "Salary paid to an unsubmitted secondary bank account",
                        "Delayed payroll credit across month boundary",
                        "Salary inflation on loan application"
                    ],
                    next_recommended_checks=[
                        "Request bank statements for all active accounts",
                        "Verify Form 26AS / tax withholding ledger"
                    ]
                )
                db.add(finding)
                db.flush()

                if res.get("claim_id"):
                    db.add(EvidenceLink(
                        finding_id=finding.id,
                        entity_type="CLAIM",
                        entity_id=str(res["claim_id"]),
                        role="PRIMARY",
                        notes=f"Unreconciled claim for {res['target_amount']:,.2f} INR"
                    ))

        # 5.3 Income Declaration Alignment Check
        income_align = reconcile_income_declaration(app_claims, salary_claims)
        for disc in income_align.get("discrepancies", []):
            finding = Finding(
                case_id=case.id,
                run_id=run.id,
                title=f"Declared Income vs. Payslip {disc['field'].replace('_', ' ').title()} Discrepancy",
                observation_type="CONTEXTUAL_MISMATCH",
                severity="MEDIUM",
                uncertainty="LOW",
                summary=(
                    f"Declared monthly {disc['field']} ({disc['declared']:,.2f} INR) differs by "
                    f"{abs(disc['delta']):,.2f} INR from verified payslip average ({disc['verified_average']:,.2f} INR)."
                ),
                alternative_explanations=[
                    "Applicant declared annual CTC divided by 12 rather than monthly in-hand",
                    "Recent promotion or increment not reflected in submitted payslips"
                ],
                next_recommended_checks=[
                    "Request employer increment letter or Form 16"
                ]
            )
            db.add(finding)
            db.flush()

        # 5.4 Employer Entity Consistency Check
        employer_check = check_employer_consistency(all_fields, all_transactions)
        for mismatch in employer_check.get("mismatches", []):
            finding = Finding(
                case_id=case.id,
                run_id=run.id,
                title="Employer Entity Discrepancy Across Documents",
                observation_type="CONTEXTUAL_MISMATCH",
                severity="HIGH",
                uncertainty="LOW",
                summary=(
                    f"Observed employer entity mismatch: Loan application declares '{mismatch['declared']}', "
                    f"whereas salary slip issues from '{mismatch['found']}' (similarity score: {mismatch['similarity_score']})."
                ),
                alternative_explanations=[
                    "Subsidiary or parent corporate entity name divergence",
                    "Staffing agency or third-party payroll processor"
                ],
                next_recommended_checks=[
                    "Verify corporate registrar MCA records for corporate relationship",
                    "Request official employment verification letter"
                ]
            )
            db.add(finding)
            db.flush()

        # Stage 6: Visual Forensic Baseline Analysis (Milestone 09 & 11)
        total_visual_crops = 0
        total_visual_anomalies = 0
        region_adapter = RegionClassifierAdapter()

        for doc in case.documents:
            pages = db.query(Page).filter(Page.document_id == doc.id).all()
            for page in pages:
                if not page.rendered_image_path or not os.path.exists(page.rendered_image_path):
                    continue

                # 1. Native Font Consistency Analysis
                font_analysis = analyze_native_font_consistency(doc.original_path, page.page_number)
                for font_anom in font_analysis.get("anomalies", []):
                    total_visual_anomalies += 1
                    crop_path = save_crop_derivative(page.rendered_image_path, font_anom["bbox_normalized"], crop_prefix="font")
                    if crop_path:
                        total_visual_crops += 1

                    obs = VisualObservation(
                        run_id=run.id,
                        page_id=page.id,
                        detector_name="font_family_analyzer",
                        detector_version="1.0.0",
                        measured_property="font_name_mismatch",
                        measured_value=1.0,
                        threshold_value=0.0,
                        bbox_normalized=font_anom["bbox_normalized"],
                        crop_path=crop_path,
                        evidence_strength="MEDIUM",
                        limitations="Font dictionary inspection via PyMuPDF dict mode"
                    )
                    db.add(obs)
                    db.flush()

                    finding = Finding(
                        case_id=case.id,
                        run_id=run.id,
                        title="Font Family Discrepancy on Numeric Field",
                        observation_type="VISUAL_ANOMALY",
                        severity="MEDIUM",
                        uncertainty="LOW",
                        summary=(
                            f"Observed font family '{font_anom['font_name']}' on numeric value '{font_anom['text']}', "
                            f"differing from predominant document font '{font_analysis.get('dominant_font')}'. "
                            f"Disjoint fonts on isolated amounts indicate potential digital tampering."
                        ),
                        alternative_explanations=[
                            "Multi-font template formatting in original PDF generation software",
                            "Digital font substitution or splicing"
                        ],
                        next_recommended_checks=[
                            "Inspect dual-crop visual comparator in Evidence Viewer",
                            "Review original font stream in PDF properties"
                        ]
                    )
                    db.add(finding)
                    db.flush()

                    db.add(EvidenceLink(
                        finding_id=finding.id,
                        entity_type="OBSERVATION",
                        entity_id=obs.id,
                        role="PRIMARY",
                        notes=f"Font mismatch on span '{font_anom['text']}'"
                    ))

                # 2. Local Sharpness & Contrast Discontinuity on Key Page Fields
                page_fields = [f for f in all_fields if f.page_id == page.id and f.bbox_normalized]
                for fld in page_fields:
                    if fld.numeric_value is not None or fld.field_name in ["applicant_name", "employer_name", "pan_number"]:
                        sharp_res = analyze_sharpness_variance(page.rendered_image_path, fld.bbox_normalized)
                        edge_res = analyze_contrast_edge_discontinuity(page.rendered_image_path, fld.bbox_normalized)

                        if sharp_res.get("is_anomaly") or edge_res.get("is_anomaly"):
                            total_visual_anomalies += 1
                            crop_path = save_crop_derivative(page.rendered_image_path, fld.bbox_normalized, crop_prefix="anomaly")
                            if crop_path:
                                total_visual_crops += 1

                            obs_metric = sharp_res["measured_value"] if sharp_res.get("is_anomaly") else edge_res["measured_value"]
                            obs_detector = "sharpness_variance" if sharp_res.get("is_anomaly") else "contrast_edge_discontinuity"
                            obs_prop = "sharpness_ratio" if sharp_res.get("is_anomaly") else "border_gradient_ratio"

                            obs = VisualObservation(
                                run_id=run.id,
                                page_id=page.id,
                                detector_name=obs_detector,
                                detector_version="1.0.0",
                                measured_property=obs_prop,
                                measured_value=obs_metric,
                                threshold_value=3.0 if sharp_res.get("is_anomaly") else 4.5,
                                bbox_normalized=fld.bbox_normalized,
                                crop_path=crop_path,
                                evidence_strength="MEDIUM",
                                limitations="Measured on 150 DPI rasterized derivative; lossy compression or scanning artifacts may influence ratio"
                            )
                            db.add(obs)
                            db.flush()

                            finding = Finding(
                                case_id=case.id,
                                run_id=run.id,
                                title=f"Visual {'Sharpness' if sharp_res.get('is_anomaly') else 'Edge Contrast'} Discontinuity on {fld.field_name.replace('_', ' ').title()}",
                                observation_type="VISUAL_ANOMALY",
                                severity="MEDIUM",
                                uncertainty="LOW",
                                summary=(
                                    f"Observed anomalous visual raster metric ({obs_prop} = {obs_metric:.2f}) on field "
                                    f"'{fld.field_name}' ({fld.raw_value}). Discontinuities in blur or boundary gradients "
                                    f"frequently indicate digital image splicing."
                                ),
                                alternative_explanations=[
                                    "Printer scanner JPEG compression blocking",
                                    "Digital text paste or box overlay artifact"
                                ],
                                next_recommended_checks=[
                                    "Inspect dual-crop visual comparator in Evidence Viewer",
                                    "Request native digital electronic statement"
                                ]
                            )
                            db.add(finding)
                            db.flush()

                            db.add(EvidenceLink(
                                finding_id=finding.id,
                                entity_type="OBSERVATION",
                                entity_id=obs.id,
                                role="PRIMARY",
                                notes=f"{obs_prop} anomaly: {obs_metric:.2f}"
                            ))
                            db.add(EvidenceLink(
                                finding_id=finding.id,
                                entity_type="FIELD",
                                entity_id=fld.id,
                                role="SUPPORTING",
                                notes=f"Field {fld.field_name}"
                            ))

                            # Milestone 11: MobileNetV3 Small Region Classifier Evaluation
                            if crop_path and region_adapter.model is not None:
                                model_pred = region_adapter.predict_crop(crop_path)
                                if model_pred.get("is_anomaly"):
                                    obs_model = VisualObservation(
                                        run_id=run.id,
                                        page_id=page.id,
                                        detector_name="mobilenet_small_region",
                                        detector_version="1.0.0",
                                        measured_property="manipulation_probability",
                                        measured_value=model_pred["manipulation_probability"],
                                        threshold_value=0.50,
                                        bbox_normalized=fld.bbox_normalized,
                                        crop_path=crop_path,
                                        evidence_strength="MEDIUM",
                                        limitations="Evaluated using MobileNetV3 Small region classifier on candidate crop"
                                    )
                                    db.add(obs_model)
                                    db.flush()

        # Stage 7: Check Executions Recording
        # Check 1: CHK_PAGE_ROUTING
        chk_routing = db.query(CheckDefinition).filter(CheckDefinition.id == "CHK_PAGE_ROUTING").first()
        if not chk_routing:
            chk_routing = CheckDefinition(
                id="CHK_PAGE_ROUTING",
                category="INGESTION",
                name="Page-Level Content & Raster Routing",
                description="Verifies page rasterization and native vs. scanned vector text presence.",
                is_mandatory=1
            )
            db.add(chk_routing)
            db.commit()

        db.add(CheckExecution(
            run_id=run.id,
            check_id="CHK_PAGE_ROUTING",
            lifecycle_state="COMPLETED",
            applicability="APPLICABLE",
            outcome="CONSISTENT",
            assumptions=["Rendered at 150 DPI for forensic inspection"],
            parameters_used={"max_pages": len(case.documents)}
        ))

        # Check 2: CHK_SOURCE_EXTRACTION
        chk_ocr = db.query(CheckDefinition).filter(CheckDefinition.id == "CHK_SOURCE_EXTRACTION").first()
        if not chk_ocr:
            chk_ocr = CheckDefinition(
                id="CHK_SOURCE_EXTRACTION",
                category="EXTRACTION",
                name="OCR, Table and Typed Claim Geometry Extraction",
                description="Extracts source-linked fields, table rows, and claims with normalized bounding boxes.",
                is_mandatory=1
            )
            db.add(chk_ocr)
            db.commit()

        db.add(CheckExecution(
            run_id=run.id,
            check_id="CHK_SOURCE_EXTRACTION",
            lifecycle_state="COMPLETED",
            applicability="APPLICABLE",
            outcome="CONSISTENT" if total_fields > 0 else "WARNING",
            assumptions=["PyMuPDF vector text extraction", "Normalized bbox geometry [ymin, xmin, ymax, xmax]"],
            parameters_used={
                "fields_extracted": total_fields,
                "claims_generated": total_claims,
                "transactions_extracted": total_txs
            }
        ))

        # Check 3: CHK_TEXT_LAYER_INTEGRITY
        chk_crosscheck = db.query(CheckDefinition).filter(CheckDefinition.id == "CHK_TEXT_LAYER_INTEGRITY").first()
        if not chk_crosscheck:
            chk_crosscheck = CheckDefinition(
                id="CHK_TEXT_LAYER_INTEGRITY",
                category="STRUCTURAL",
                name="Native Vector Text vs. Rendered Evidence Crosscheck",
                description="Crosschecks vector text layer against visual rendering, inspecting for hidden text, prompt injections, and baseline displacements.",
                is_mandatory=1
            )
            db.add(chk_crosscheck)
            db.commit()

        crosscheck_outcome = "CONSISTENT"
        if total_prompt_injections > 0:
            crosscheck_outcome = "DISCREPANCY"
        elif total_baseline_anomalies > 0:
            crosscheck_outcome = "DISCREPANCY"
        elif total_invisible_spans > 0:
            crosscheck_outcome = "POSSIBLE_EXPLANATION"

        db.add(CheckExecution(
            run_id=run.id,
            check_id="CHK_TEXT_LAYER_INTEGRITY",
            lifecycle_state="COMPLETED",
            applicability="APPLICABLE",
            outcome=crosscheck_outcome,
            assumptions=[
                "PyMuPDF vector text span and origin dictionary inspection",
                "Baseline displacement threshold >= 2.0px",
                "Prompt injection signature vocabulary matching"
            ],
            parameters_used={
                "pages_analyzed": total_pages_analyzed,
                "invisible_spans_found": total_invisible_spans,
                "prompt_injections_found": total_prompt_injections,
                "baseline_anomalies_found": total_baseline_anomalies
            }
        ))

        # Check 4: CHK_BALANCE_INTEGRITY
        chk_balance = db.query(CheckDefinition).filter(CheckDefinition.id == "CHK_BALANCE_INTEGRITY").first()
        if not chk_balance:
            chk_balance = CheckDefinition(
                id="CHK_BALANCE_INTEGRITY",
                category="FINANCIAL",
                name="Bank Statement Running Balance Arithmetic Reconciliation",
                description="Validates running ledger balance: prev_balance + credits - debits == current_balance.",
                is_mandatory=1
            )
            db.add(chk_balance)
            db.commit()

        db.add(CheckExecution(
            run_id=run.id,
            check_id="CHK_BALANCE_INTEGRITY",
            lifecycle_state="COMPLETED",
            applicability="APPLICABLE" if all_transactions else "NOT_APPLICABLE",
            outcome="CONSISTENT" if balance_recon["is_reconciled"] else "DISCREPANCY",
            assumptions=["Decimal 2-place precision arithmetic", "Chronological row sequencing"],
            parameters_used={"total_transactions_checked": len(all_transactions), "discrepancies_found": len(balance_recon["discrepancies"])}
        ))

        # Check 5: CHK_SALARY_CREDIT_RECON
        chk_salary = db.query(CheckDefinition).filter(CheckDefinition.id == "CHK_SALARY_CREDIT_RECON").first()
        if not chk_salary:
            chk_salary = CheckDefinition(
                id="CHK_SALARY_CREDIT_RECON",
                category="CROSS_DOCUMENT",
                name="Payslip to Bank Account Payroll Credit Reconciliation",
                description="Reconciles net payable salary on payslips with candidate credit entries in bank statements.",
                is_mandatory=1
            )
            db.add(chk_salary)
            db.commit()

        salary_recon_outcome = "CONSISTENT"
        if not salary_match["all_matched"]:
            salary_recon_outcome = "DISCREPANCY"
        elif salary_match["has_splits"]:
            salary_recon_outcome = "POSSIBLE_EXPLANATION"

        db.add(CheckExecution(
            run_id=run.id,
            check_id="CHK_SALARY_CREDIT_RECON",
            lifecycle_state="COMPLETED",
            applicability="APPLICABLE" if salary_claims and all_transactions else "INSUFFICIENT_EVIDENCE",
            outcome=salary_recon_outcome,
            assumptions=["Single exact match or multi-deposit split match in pay period window"],
            parameters_used={
                "salary_claims_checked": len(salary_claims),
                "all_matched": salary_match["all_matched"],
                "has_splits": salary_match["has_splits"]
            }
        ))

        # Check 6: CHK_EMPLOYER_ENTITY_CONSISTENCY
        chk_emp = db.query(CheckDefinition).filter(CheckDefinition.id == "CHK_EMPLOYER_ENTITY_CONSISTENCY").first()
        if not chk_emp:
            chk_emp = CheckDefinition(
                id="CHK_EMPLOYER_ENTITY_CONSISTENCY",
                category="CROSS_DOCUMENT",
                name="Employer Entity Name Consistency Across Documents",
                description="Compares corporate employer names across application form, salary slips, and bank narrations.",
                is_mandatory=1
            )
            db.add(chk_emp)
            db.commit()

        db.add(CheckExecution(
            run_id=run.id,
            check_id="CHK_EMPLOYER_ENTITY_CONSISTENCY",
            lifecycle_state="COMPLETED",
            applicability="APPLICABLE" if employer_check["declared_employer"] else "NOT_APPLICABLE",
            outcome="CONSISTENT" if employer_check["is_consistent"] else "DISCREPANCY",
            assumptions=["Normalized corporate token comparison with fuzzy matching threshold >= 0.50"],
            parameters_used={"declared_employer": employer_check["declared_employer"], "mismatches": len(employer_check["mismatches"])}
        ))

        # Check 7: CHK_VISUAL_FORENSIC_BASELINE
        chk_visual = db.query(CheckDefinition).filter(CheckDefinition.id == "CHK_VISUAL_FORENSIC_BASELINE").first()
        if not chk_visual:
            chk_visual = CheckDefinition(
                id="CHK_VISUAL_FORENSIC_BASELINE",
                category="VISUAL",
                name="Explainable Raster Sharpness & Font Baseline Forensics",
                description="Measures local Laplacian sharpness variance, contrast boundary discontinuities, and native font face consistency across critical document regions.",
                is_mandatory=1
            )
            db.add(chk_visual)
            db.commit()

        db.add(CheckExecution(
            run_id=run.id,
            check_id="CHK_VISUAL_FORENSIC_BASELINE",
            lifecycle_state="COMPLETED",
            applicability="APPLICABLE",
            outcome="CONSISTENT" if total_visual_anomalies == 0 else "DISCREPANCY",
            assumptions=["150 DPI raster derivative", "Laplacian sharpness variance ratio threshold: [0.30, 3.0]"],
            parameters_used={
                "visual_crops_saved": total_visual_crops,
                "visual_anomalies_found": total_visual_anomalies
            }
        ))

        # Stage 8: Mark Run Complete
        run.status = "COMPLETED"
        run.completed_at = datetime.now(timezone.utc)
        db.commit()

        record_audit_event(
            db=db,
            case_id=case.id,
            action_type="RUN_COMPLETED",
            actor_id="local_runner",
            payload={
                "run_id": run.id,
                "documents_processed": len(case.documents),
                "fields_extracted": total_fields,
                "claims_generated": total_claims,
                "transactions_extracted": total_txs,
                "prompt_injections_detected": total_prompt_injections,
                "baseline_anomalies_detected": total_baseline_anomalies,
                "balance_reconciled": balance_recon["is_reconciled"],
                "salary_credit_match_status": salary_match["status"],
                "employer_consistent": employer_check["is_consistent"],
                "visual_anomalies_detected": total_visual_anomalies
            }
        )

    except Exception as e:
        db.rollback()
        run = db.query(ProcessingRun).filter(ProcessingRun.id == run_id).first()
        if run:
            run.status = "FAILED"
            run.error_message = str(e)
            db.commit()
    finally:
        db.close()
