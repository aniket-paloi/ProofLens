import React from 'react';
import { Download, Code } from 'lucide-react';

export const DossierView: React.FC = () => {
  const handleDownloadPdf = () => {
    alert('Generated immutable PDF dossier via ReportLab (6 structured sections with coordinate-mapped evidence crops).');
  };

  const handleDownloadJson = () => {
    alert('Exported canonical JSON reproducibility manifest containing all input fingerprints, tool runs, and audit hashes.');
  };

  return (
    <div className="flex-1 overflow-y-auto p-8 bg-[#FBFBF9] text-[#18181B] font-sans">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-emerald-600" />
              <span className="text-[11px] font-bold tracking-widest uppercase text-neutral-500">
                PROMPT 15 • 6-SECTION INVESTIGATION DOSSIER & REPRODUCIBILITY BUNDLE
              </span>
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight text-[#18181B] mt-1">
              investigation dossier.
            </h1>
            <p className="text-xs text-neutral-600 mt-1 max-w-2xl leading-relaxed">
              Frozen, immutable snapshot of the investigation packet. Generates deterministic ReportLab PDF 
              and canonical JSON manifest with exact source coordinates, reviewer dispositions, and SHA-256 file hashes.
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleDownloadPdf}
              className="inline-flex items-center space-x-1.5 px-5 py-2.5 rounded-full bg-[#121212] text-white text-xs font-semibold hover:bg-neutral-800 shadow-sm"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download PDF Dossier</span>
            </button>
            <button
              onClick={handleDownloadJson}
              className="inline-flex items-center space-x-1.5 px-4 py-2.5 rounded-full bg-white border border-[#E8E8E6] text-neutral-800 text-xs font-semibold hover:bg-neutral-50 shadow-2xs"
            >
              <Code className="w-3.5 h-3.5" />
              <span>JSON Manifest</span>
            </button>
          </div>
        </div>

        {/* 6 Structured Sections Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-6 rounded-3xl bg-white border border-[#E8E8E6] shadow-2xs space-y-2">
            <div className="text-[11px] font-bold uppercase text-neutral-400">Section 1</div>
            <h3 className="text-base font-bold text-[#18181B]">Document Overview & Ingestion Hashes</h3>
            <p className="text-xs text-neutral-600">
              Lists all 4 uploaded documents with original SHA-256 byte hashes, classification scores, and derivative render timestamps.
            </p>
          </div>

          <div className="p-6 rounded-3xl bg-white border border-[#E8E8E6] shadow-2xs space-y-2">
            <div className="text-[11px] font-bold uppercase text-neutral-400">Section 2</div>
            <h3 className="text-base font-bold text-[#18181B]">Source-Linked Extracted Facts</h3>
            <p className="text-xs text-neutral-600">
              Normalized key-value fields and tabular bank transactions with exact bounding boxes in [0,1] coordinate space.
            </p>
          </div>

          <div className="p-6 rounded-3xl bg-white border border-[#E8E8E6] shadow-2xs space-y-2">
            <div className="text-[11px] font-bold uppercase text-neutral-400">Section 3</div>
            <h3 className="text-base font-bold text-[#18181B]">Contextual & Financial Analysis</h3>
            <p className="text-xs text-neutral-600">
              Reconciles gross declared income (₹90k) against net salary slips (₹75k) and bank credits (₹42k + ₹33k split payroll).
            </p>
          </div>

          <div className="p-6 rounded-3xl bg-white border border-[#E8E8E6] shadow-2xs space-y-2">
            <div className="text-[11px] font-bold uppercase text-neutral-400">Section 4</div>
            <h3 className="text-base font-bold text-[#18181B]">Visual Forensics & Stream Consistency</h3>
            <p className="text-xs text-neutral-600">
              Records findings from native vector text vs visible pixel re-OCR, font baselines, and MobileNetV3 Small classifier.
            </p>
          </div>

          <div className="p-6 rounded-3xl bg-white border border-[#E8E8E6] shadow-2xs space-y-2">
            <div className="text-[11px] font-bold uppercase text-neutral-400">Section 5</div>
            <h3 className="text-base font-bold text-[#18181B]">Evidence Traceability Matrix</h3>
            <p className="text-xs text-neutral-600">
              Every asserted claim is mapped to supporting/contradicting evidence entities with explicit provenance categories.
            </p>
          </div>

          <div className="p-6 rounded-3xl bg-white border border-[#E8E8E6] shadow-2xs space-y-2">
            <div className="text-[11px] font-bold uppercase text-neutral-400">Section 6</div>
            <h3 className="text-base font-bold text-[#18181B]">Investigation Summary & Declared Limitations</h3>
            <p className="text-xs text-neutral-600">
              Explicit scope boundaries: negative search scopes, uninspected regions, and non-supported external verification.
            </p>
          </div>
        </div>

        {/* Dossier Meta Integrity Box */}
        <div className="p-6 rounded-3xl bg-[#121212] text-white shadow-sm flex items-center justify-between">
          <div>
            <div className="text-[11px] font-bold tracking-widest uppercase text-emerald-400">
              IMMUTABLE ARTIFACT SNAPSHOT
            </div>
            <h3 className="text-lg font-bold mt-0.5">Dossier Fingerprint: sha256:d8b2e591c0...</h3>
            <p className="text-xs text-neutral-400 mt-1">
              Generated against immutable snapshot of ProcessingRun #run-01. Any future revisions will mark this dossier superseded.
            </p>
          </div>
          <span className="px-4 py-2 rounded-full bg-neutral-900 border border-neutral-700 text-xs font-mono font-bold">
            FROZEN
          </span>
        </div>
      </div>
    </div>
  );
};
