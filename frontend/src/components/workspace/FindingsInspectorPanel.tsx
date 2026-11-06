import React, { useState } from 'react';
import {
  AlertCircle,
  CheckCircle2,
  GitBranch,
  Info,
  ArrowRight,
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
  const confidenceSlider = 75;
  const [submitting, setSubmitting] = useState<boolean>(false);

  if (!activeClaim) {
    return (
      <div className="w-96 h-full bg-white border-l border-slate-200 p-6 flex flex-col items-center justify-center text-center text-slate-400 select-none">
        <GitBranch className="w-8 h-8 text-slate-300 mb-2" />
        <div className="text-sm font-semibold text-slate-700">No Claim Selected</div>
        <div className="text-xs text-slate-400 mt-1">
          Select a claim from Panel 1 or click a highlighted box in the Evidence Viewer to inspect details.
        </div>
      </div>
    );
  }

  const isDiscrepancy = activeClaim.status === 'DISCREPANCY';

  const handleAction = async (disposition: string) => {
    setSubmitting(true);
    try {
      await onSubmitReview(
        activeClaim.id,
        disposition,
        reviewerNotes || `Reviewer disposition: ${disposition} (confidence ${confidenceSlider}%)`
      );
      setReviewerNotes('');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="w-96 h-full bg-white border-l border-slate-200 flex flex-col flex-shrink-0 select-none overflow-y-auto">
      {/* Panel 3 Header */}
      <div className="p-4 border-b border-slate-200 flex items-center justify-between">
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
            Panel 3 • Findings & Reconciliations
          </span>
          <h2 className="text-sm font-bold text-slate-900 mt-0.5">Quick View Inspector</h2>
        </div>

        {/* Status Pill Badge (Thoropass / Transaction Quick View Inspired) */}
        {isDiscrepancy ? (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-red-50 text-red-700 border border-red-200">
            <AlertCircle className="w-3.5 h-3.5" />
            Unreconciled
          </span>
        ) : (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Reconciled
          </span>
        )}
      </div>

      <div className="p-4 space-y-5">
        {/* RECONCILIATION MATCH STATUS NODE TREE (Reproducing Images 4 & 5!) */}
        <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
              <GitBranch className="w-3.5 h-3.5 text-indigo-600" />
              Reconciliation Match Status
            </span>
          </div>

          {/* Node Graph Container */}
          <div className="space-y-2 mt-3 font-sans">
            {/* Root Node: Declared Claim */}
            <div className="p-2 rounded-lg bg-white border border-slate-200 shadow-subtle flex items-center justify-between text-xs">
              <div className="flex items-center space-x-2">
                <span className="w-2 h-2 rounded-full bg-indigo-600"></span>
                <span className="font-semibold text-slate-800">Declared Claim:</span>
              </div>
              <span className="font-mono font-bold text-slate-900">{activeClaim.declaredValue}</span>
            </div>

            {/* Tree Branch Connectors */}
            <div className="pl-4 border-l-2 border-slate-200 ml-3 space-y-2 py-1">
              {/* Branch 1: Salary Slip Verification */}
              <div className="relative flex items-center justify-between p-2 rounded-lg bg-white border border-slate-200 text-xs shadow-subtle">
                <div className="flex items-center space-x-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-red-500"></span>
                  <span className="text-slate-600 text-[11px]">Salary Slip (Base)</span>
                </div>
                <div className="flex items-center space-x-1">
                  <span className="font-mono text-[11px] text-slate-700">₹48,000</span>
                  <span className="text-[9px] px-1 py-0.2 rounded bg-red-100 text-red-700 font-bold">
                    !
                  </span>
                </div>
              </div>

              {/* Branch 2: Bank Statement Primary Credit */}
              <div className="relative flex items-center justify-between p-2 rounded-lg bg-white border border-slate-200 text-xs shadow-subtle">
                <div className="flex items-center space-x-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-red-500"></span>
                  <span className="text-slate-600 text-[11px]">Bank Statement Credit</span>
                </div>
                <div className="flex items-center space-x-1">
                  <span className="font-mono text-[11px] font-bold text-red-600">{activeClaim.extractedValue}</span>
                  <span className="text-[9px] px-1 py-0.2 rounded bg-red-100 text-red-700 font-bold">
                    !
                  </span>
                </div>
              </div>

              {/* Branch 3: Candidate Split Payment (+2 Days) */}
              <div className="relative flex items-center justify-between p-2 rounded-lg bg-white border border-slate-200 text-xs shadow-subtle">
                <div className="flex items-center space-x-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                  <span className="text-slate-600 text-[11px]">Split Incentive (+2d)</span>
                </div>
                <div className="flex items-center space-x-1">
                  <span className="font-mono text-[11px] text-amber-700">₹33,000</span>
                  <span className="text-[9px] px-1 py-0.2 rounded bg-amber-100 text-amber-800 font-bold">
                    candidate
                  </span>
                </div>
              </div>
            </div>

            {/* Tree Summary Footer (Exact match to Image 4: '● 1 match ● 2 exceptions') */}
            <div className="pt-2 border-t border-slate-200 flex items-center space-x-4 text-[11px] font-medium text-slate-600">
              <span className="flex items-center gap-1 text-emerald-700">
                <span className="w-2 h-2 rounded-full bg-emerald-500"></span> 1 candidate match
              </span>
              <span className="flex items-center gap-1 text-red-700">
                <span className="w-2 h-2 rounded-full bg-red-500"></span> 2 exceptions
              </span>
            </div>
          </div>
        </div>

        {/* STRUCTURED RECORD BREAKDOWN TABLE */}
        <div>
          <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2">
            Claim Audit Record
          </div>
          <div className="rounded-xl border border-slate-200 divide-y divide-slate-100 text-xs bg-white">
            <div className="p-2.5 flex items-center justify-between">
              <span className="text-slate-500">Unique ID</span>
              <span className="font-mono font-medium text-slate-800">{activeClaim.id}</span>
            </div>
            <div className="p-2.5 flex items-center justify-between">
              <span className="text-slate-500">Declared Amount</span>
              <span className="font-mono font-bold text-slate-900">{activeClaim.declaredValue}</span>
            </div>
            <div className="p-2.5 flex items-center justify-between">
              <span className="text-slate-500">Extracted Amount</span>
              <span className="font-mono font-bold text-red-600">{activeClaim.extractedValue}</span>
            </div>
            <div className="p-2.5 flex items-center justify-between">
              <span className="text-slate-500">Discrepancy Delta</span>
              <span className="font-mono font-bold text-red-600">
                {activeClaim.discrepancyDelta || '-₹48,000 (-53.3%)'}
              </span>
            </div>
            <div className="p-2.5 flex items-center justify-between">
              <span className="text-slate-500">Source Document</span>
              <span className="text-slate-700 truncate max-w-[160px]">{activeClaim.sourceDoc}</span>
            </div>
            <div className="p-2.5 flex items-center justify-between">
              <span className="text-slate-500">Target Statement</span>
              <span className="text-slate-700 truncate max-w-[160px]">{activeClaim.targetDoc}</span>
            </div>
            <div className="p-2.5 flex items-center justify-between">
              <span className="text-slate-500">Extraction Engine</span>
              <span className="font-mono text-[11px] text-slate-600">PyMuPDF + PaddleOCR</span>
            </div>
          </div>
        </div>

        {/* NON-ACCUSATORY ALTERNATIVE EXPLANATIONS */}
        <div className="p-3.5 rounded-xl bg-indigo-50/50 border border-indigo-100 text-xs">
          <div className="flex items-center space-x-1.5 text-indigo-900 font-bold mb-2">
            <Info className="w-4 h-4 text-indigo-600" />
            <span>Alternative Hypotheses</span>
          </div>
          <ul className="space-y-1.5 text-slate-600 text-[11px] leading-relaxed list-disc list-inside">
            <li>
              <strong className="text-slate-800">Split Payroll Structure:</strong> Secondary credit of ₹33,000 recorded 2 days later may satisfy total earnings.
            </li>
            <li>
              <strong className="text-slate-800">Annual Bonus Rollup:</strong> Declared gross may incorporate annualized variable allowance.
            </li>
          </ul>
        </div>

        {/* NEXT RECOMMENDED CHECKS */}
        <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs">
          <div className="font-bold text-slate-800 mb-1 flex items-center gap-1.5">
            <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
            <span>Next Recommended Step</span>
          </div>
          <p className="text-[11px] text-slate-600 leading-relaxed">
            Examine Month 2 covering statement to verify if split payroll behavior is regular or an irregular deposit.
          </p>
        </div>

        {/* REVIEWER SOVEREIGNTY ACTIONS */}
        <div className="pt-2 border-t border-slate-200 space-y-3">
          <div className="flex items-center justify-between text-xs">
            <span className="font-bold text-slate-800">Reviewer Disposition</span>
            <span className="text-[10px] text-slate-400 font-mono">Immutable Audit Chain</span>
          </div>

          <textarea
            rows={2}
            placeholder="Add reviewer rationale or notes for audit trail..."
            value={reviewerNotes}
            onChange={(e) => setReviewerNotes(e.target.value)}
            className="w-full text-xs p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
          />

          {/* Action Button Row */}
          <div className="grid grid-cols-2 gap-2 text-xs">
            <button
              onClick={() => handleAction('CONFIRMED_DISCREPANCY')}
              disabled={submitting}
              className="py-2 px-3 rounded-lg bg-red-600 text-white font-semibold hover:bg-red-700 transition-colors shadow-sm disabled:opacity-50 text-center"
            >
              Flag Discrepancy
            </button>
            <button
              onClick={() => handleAction('DISMISSED_EXPLAINED')}
              disabled={submitting}
              className="py-2 px-3 rounded-lg bg-emerald-600 text-white font-semibold hover:bg-emerald-700 transition-colors shadow-sm disabled:opacity-50 text-center"
            >
              Mark Explained
            </button>
          </div>

          <button
            onClick={() => handleAction('REQUEST_ADDITIONAL_DOCS')}
            disabled={submitting}
            className="w-full py-1.5 rounded-lg border border-amber-300 bg-amber-50 text-amber-800 text-[11px] font-semibold hover:bg-amber-100 transition-colors text-center"
          >
            Request Form 16 / Additional Evidence
          </button>
        </div>
      </div>
    </div>
  );
};
