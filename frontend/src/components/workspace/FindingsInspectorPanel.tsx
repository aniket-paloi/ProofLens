import React, { useState } from 'react';
import {
  AlertCircle,
  CheckCircle2,
  GitBranch,
  Info,
  ArrowRight,
  ShieldCheck,
} from 'lucide-react';
import { InvestigationClaimItem } from './DocumentsListPanel';

interface FindingsInspectorPanelProps {
  activeClaim: InvestigationClaimItem | null;
  onSubmitReview: (claimId: string, disposition: string, reason: string) => Promise<void>;
}

export const FindingsInspectorPanel: React.FC<FindingsInspectorPanelProps> = ({
  activeClaim,
  onSubmitReview,
}) => {
  const [reviewerNotes, setReviewerNotes] = useState<string>('');
  const [confidenceSlider, setConfidenceSlider] = useState<number>(85);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [lastActionMsg, setLastActionMsg] = useState<string | null>(null);

  if (!activeClaim) {
    return (
      <div className="w-96 h-full bg-white border-l border-[#E8E8E6] p-6 flex flex-col items-center justify-center text-center text-neutral-400 select-none">
        <GitBranch className="w-8 h-8 text-neutral-300 mb-2" />
        <div className="text-sm font-semibold text-[#18181B]">no claim selected.</div>
        <div className="text-xs text-neutral-400 mt-1 max-w-xs">
          Select a claim from Panel 1 or click a highlighted box in the Evidence Viewer to inspect details and commit audit decisions.
        </div>
      </div>
    );
  }

  const isDiscrepancy = activeClaim.status === 'DISCREPANCY';

  const handleAction = async (disposition: string) => {
    setSubmitting(true);
    setLastActionMsg(null);
    try {
      await onSubmitReview(
        activeClaim.id,
        disposition,
        reviewerNotes || `Reviewer disposition: ${disposition} (confidence ${confidenceSlider}%)`
      );
      setReviewerNotes('');
      setLastActionMsg(`Disposition recorded: ${disposition}`);
      setTimeout(() => setLastActionMsg(null), 3000);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="w-96 h-full bg-white border-l border-[#E8E8E6] flex flex-col flex-shrink-0 select-none overflow-y-auto">
      {/* Panel 3 Header */}
      <div className="p-4 border-b border-[#E8E8E6] flex items-center justify-between">
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider text-neutral-400">
            PANEL 3 • RECONCILIATIONS
          </span>
          <h2 className="text-sm font-bold text-[#18181B] mt-0.5">quick inspector.</h2>
        </div>
        <div className="flex items-center space-x-1 text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200 text-[10px] font-bold">
          <ShieldCheck className="w-3 h-3" />
          <span>ZERO-ACCUSATION</span>
        </div>
      </div>

      <div className="p-5 space-y-5 flex-1">
        {lastActionMsg && (
          <div className="p-3 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>{lastActionMsg}</span>
          </div>
        )}

        {/* Claim Overview Card */}
        <div className="p-4 rounded-3xl bg-[#FBFBF9] border border-[#E8E8E6] space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono font-semibold uppercase px-2.5 py-0.5 rounded-full bg-white border border-[#E8E8E6] text-neutral-600">
              {activeClaim.category}
            </span>
            <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${
              isDiscrepancy
                ? 'bg-rose-50 text-rose-800 border-rose-200'
                : 'bg-emerald-50 text-emerald-800 border-emerald-200'
            }`}>
              {activeClaim.status}
            </span>
          </div>

          <h3 className="font-bold text-xs text-[#18181B] leading-snug">
            {activeClaim.title}
          </h3>

          <p className="text-xs text-neutral-600 leading-relaxed">
            {activeClaim.summary}
          </p>

          <div className="pt-2 border-t border-[#E8E8E6] grid grid-cols-2 gap-2 text-[11px] font-mono">
            <div className="p-2 rounded-2xl bg-white border border-[#E8E8E6]">
              <span className="text-[10px] text-neutral-400 block">Declared</span>
              <span className="font-bold text-[#18181B]">{activeClaim.declaredValue}</span>
            </div>
            <div className="p-2 rounded-2xl bg-white border border-[#E8E8E6]">
              <span className="text-[10px] text-neutral-400 block">Observed</span>
              <span className={`font-bold ${isDiscrepancy ? 'text-rose-700' : 'text-emerald-700'}`}>
                {activeClaim.extractedValue}
              </span>
            </div>
          </div>
        </div>

        {/* Multi-Document Match Status Node Tree */}
        <div className="p-4 rounded-3xl bg-white border border-[#E8E8E6] space-y-3">
          <div className="text-[10px] font-bold uppercase tracking-wider text-neutral-400">
            Provenance Lineage Tree
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex items-center space-x-2 p-2 rounded-2xl bg-[#FBFBF9] border border-[#E8E8E6]">
              <div className="w-2 h-2 rounded-full bg-neutral-800" />
              <span className="font-medium text-neutral-700 truncate">Application Declaration (₹90,000)</span>
            </div>

            <div className="flex items-center justify-center text-neutral-300">
              <ArrowRight className="w-3.5 h-3.5 rotate-90" />
            </div>

            <div className="flex items-center space-x-2 p-2 rounded-2xl bg-[#FBFBF9] border border-[#E8E8E6]">
              <div className="w-2 h-2 rounded-full bg-neutral-800" />
              <span className="font-medium text-neutral-700 truncate">Salary Slip Month 1 (₹75,000 Net)</span>
            </div>

            <div className="flex items-center justify-center text-neutral-300">
              <ArrowRight className="w-3.5 h-3.5 rotate-90" />
            </div>

            <div className="p-2.5 rounded-2xl bg-amber-50/60 border border-amber-200 space-y-1">
              <div className="flex items-center justify-between text-[11px] font-semibold text-amber-900">
                <span>Split Payroll Candidate (₹42k + ₹33k)</span>
                <span className="text-[10px] font-mono text-amber-700">Matches 100%</span>
              </div>
              <p className="text-[10px] text-amber-800">
                Two credits within 48h from Apex FinTech match declared net disbursement.
              </p>
            </div>
          </div>
        </div>

        {/* Reviewer Disposition Section */}
        <div className="p-4 rounded-3xl bg-[#FBFBF9] border border-[#E8E8E6] space-y-3">
          <div className="text-[10px] font-bold uppercase tracking-wider text-neutral-400">
            Reviewer Disposition & Hashing
          </div>

          <div className="space-y-1">
            <label className="text-[11px] font-semibold text-neutral-700 block">
              Confidence Calibration: {confidenceSlider}%
            </label>
            <input
              type="range"
              min="50"
              max="100"
              value={confidenceSlider}
              onChange={(e) => setConfidenceSlider(Number(e.target.value))}
              className="w-full accent-[#121212] bg-[#E8E8E6] rounded-lg h-1.5 cursor-pointer"
            />
          </div>

          <div>
            <label className="text-[11px] font-semibold text-neutral-700 block mb-1">
              Audit Note / Justification
            </label>
            <textarea
              rows={2}
              value={reviewerNotes}
              onChange={(e) => setReviewerNotes(e.target.value)}
              placeholder="e.g. Split direct deposit verified against employment contract appendix..."
              className="w-full text-xs p-3 rounded-2xl bg-white border border-[#E8E8E6] text-[#18181B] focus:outline-none focus:ring-1 focus:ring-[#121212] resize-none"
            />
          </div>

          <div className="space-y-2 pt-1">
            <button
              disabled={submitting}
              onClick={() => handleAction('CONFIRMED_DISCREPANCY')}
              className="w-full py-2.5 rounded-full text-xs font-semibold bg-rose-600 text-white hover:bg-rose-700 transition-colors shadow-xs disabled:opacity-50 flex items-center justify-center gap-1.5"
            >
              <AlertCircle className="w-3.5 h-3.5" />
              <span>Confirm Discrepancy Exception</span>
            </button>

            <button
              disabled={submitting}
              onClick={() => handleAction('DISMISSED_EXPLAINED')}
              className="w-full py-2.5 rounded-full text-xs font-semibold bg-[#121212] text-white hover:bg-neutral-800 transition-colors shadow-xs disabled:opacity-50 flex items-center justify-center gap-1.5"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Dismiss as Explained (Reconciled)</span>
            </button>

            <button
              disabled={submitting}
              onClick={() => handleAction('CUSTOMER_INQUIRY')}
              className="w-full py-2.5 rounded-full text-xs font-semibold bg-white border border-[#E8E8E6] text-neutral-800 hover:bg-[#F4F4F2] transition-colors disabled:opacity-50 flex items-center justify-center gap-1.5"
            >
              <Info className="w-3.5 h-3.5" />
              <span>Mark for Customer Inquiry</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
