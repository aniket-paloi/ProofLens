import React from 'react';
import {
  AlertCircle,
  CheckCircle2,
  ArrowRight,
  ShieldCheck,
  FileText,
} from 'lucide-react';
import { Case } from '../../types';

interface DashboardOverviewProps {
  cases: Case[];
  activeCase: Case | null;
  onSelectCase: (caseId: string) => void;
  onOpenWorkspace: () => void;
  onNewCase: () => void;
}

export const DashboardOverview: React.FC<DashboardOverviewProps> = ({
  cases,
  activeCase,
  onSelectCase,
  onOpenWorkspace,
  onNewCase,
}) => {
  return (
    <div className="flex-1 h-[calc(100vh-4rem)] overflow-y-auto p-8 bg-slate-50 select-none">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Top Header Banner */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 text-xs font-semibold text-indigo-600 mb-1">
              <span className="w-2 h-2 rounded-full bg-indigo-600 animate-subtle-pulse" />
              <span className="uppercase tracking-wider">Enterprise Compliance & Investigation</span>
            </div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              Program & Reconciliation Overview
            </h1>
            <p className="text-xs text-slate-500 mt-1">
              Real-time multi-document evidence verification, cross-ledger arithmetic reconciliation, and tamper auditing.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={onNewCase}
              className="px-4 py-2 text-xs font-semibold rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 shadow-sm"
            >
              New Case Packet
            </button>
            <button
              onClick={onOpenWorkspace}
              className="inline-flex items-center space-x-1.5 px-4 py-2 text-xs font-semibold rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm shadow-indigo-600/30"
            >
              <span>Launch 3-Panel Workspace</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* METRICS ROW (Inspired by Thoropass Image 1 & Settlement Image 3) */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {/* Metric 1 */}
          <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-subtle flex flex-col justify-between">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="font-semibold uppercase tracking-wider text-[10px]">Total Controls</span>
              <div className="w-6 h-6 rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold text-xs">
                ◎
              </div>
            </div>
            <div className="my-3">
              <div className="text-2xl font-bold text-slate-900">24</div>
              <div className="text-[11px] text-slate-500 mt-0.5">Unified Packet Claims</div>
            </div>
            <div className="flex items-center gap-1 text-[11px] text-red-600 font-medium">
              <AlertCircle className="w-3 h-3" />
              <span>2 Flagged Discrepancies</span>
            </div>
          </div>

          {/* Metric 2 */}
          <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-subtle flex flex-col justify-between">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="font-semibold uppercase tracking-wider text-[10px]">Reconciliation</span>
              <div className="w-6 h-6 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-xs">
                ✓
              </div>
            </div>
            <div className="my-3">
              <div className="text-2xl font-bold text-slate-900">87.5%</div>
              <div className="text-[11px] text-slate-500 mt-0.5">Cross-Ledger Match Rate</div>
            </div>
            <div className="flex items-center gap-1 text-[11px] text-emerald-700 font-medium">
              <CheckCircle2 className="w-3 h-3" />
              <span>1 Candidate Split Match</span>
            </div>
          </div>

          {/* Metric 3 */}
          <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-subtle flex flex-col justify-between">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="font-semibold uppercase tracking-wider text-[10px]">Documents</span>
              <FileText className="w-4 h-4 text-slate-400" />
            </div>
            <div className="my-3">
              <div className="text-2xl font-bold text-slate-900">4</div>
              <div className="text-[11px] text-slate-500 mt-0.5">Submitted PDF Files</div>
            </div>
            <div className="text-[11px] text-slate-500">
              App + 2 Slips + Statement
            </div>
          </div>

          {/* Metric 4 */}
          <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-subtle flex flex-col justify-between">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="font-semibold uppercase tracking-wider text-[10px]">Text Layer</span>
              <div className="w-6 h-6 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-xs">
                @
              </div>
            </div>
            <div className="my-3">
              <div className="text-2xl font-bold text-slate-900">100%</div>
              <div className="text-[11px] text-slate-500 mt-0.5">OCR Alignment Score</div>
            </div>
            <div className="text-[11px] text-emerald-700 font-medium">
              0 Hidden Text Injections
            </div>
          </div>

          {/* Metric 5 */}
          <div className="p-5 rounded-xl bg-white border border-slate-200 shadow-subtle flex flex-col justify-between">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="font-semibold uppercase tracking-wider text-[10px]">Integrity</span>
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
            </div>
            <div className="my-3">
              <div className="text-2xl font-bold text-slate-900">SHA-256</div>
              <div className="text-[11px] text-slate-500 mt-0.5">Hash Chain Verified</div>
            </div>
            <div className="text-[11px] text-emerald-700 font-medium">
              Offline Retained Checkpoint
            </div>
          </div>
        </div>

        {/* MIDDLE SECTION: FRAMEWORK HEALTH & PIPELINE */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Framework Health Card 1 */}
          <div className="p-6 rounded-xl bg-white border border-slate-200 shadow-subtle flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-0.5 rounded bg-blue-50 text-blue-700 text-xs font-bold font-mono">
                    RULE-01
                  </span>
                  <h3 className="font-bold text-sm text-slate-900">Financial Arithmetic Reconciliation</h3>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-400" />
              </div>

              <div className="space-y-2 mb-4">
                <div className="flex items-center justify-between text-xs text-slate-500">
                  <span>Reconciliation Coverage</span>
                  <span className="font-bold text-slate-800">83%</span>
                </div>
                <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-indigo-600 rounded-full" style={{ width: '83%' }} />
                </div>
              </div>

              <div className="space-y-1.5 pt-3 border-t border-slate-100 text-xs">
                <div className="flex items-center justify-between text-slate-600">
                  <span className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-red-500" />
                    Needs Attention (Salary Discrepancy)
                  </span>
                  <span className="font-bold text-slate-800 font-mono">1</span>
                </div>
                <div className="flex items-center justify-between text-slate-600">
                  <span className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-emerald-500" />
                    Healthy (Reconciled Transactions)
                  </span>
                  <span className="font-bold text-slate-800 font-mono">5</span>
                </div>
                <div className="flex items-center justify-between text-slate-600">
                  <span className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-amber-400" />
                    In Review (Delayed Candidate Credit)
                  </span>
                  <span className="font-bold text-slate-800 font-mono">1</span>
                </div>
              </div>
            </div>
          </div>

          {/* Framework Health Card 2 */}
          <div className="p-6 rounded-xl bg-white border border-slate-200 shadow-subtle flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 text-xs font-bold font-mono">
                    RULE-02
                  </span>
                  <h3 className="font-bold text-sm text-slate-900">Visual Forensics & Baseline Check</h3>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-400" />
              </div>

              <div className="space-y-2 mb-4">
                <div className="flex items-center justify-between text-xs text-slate-500">
                  <span>Raster Sharpness & Font Tolerance</span>
                  <span className="font-bold text-slate-800">96%</span>
                </div>
                <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-emerald-600 rounded-full" style={{ width: '96%' }} />
                </div>
              </div>

              <div className="space-y-1.5 pt-3 border-t border-slate-100 text-xs">
                <div className="flex items-center justify-between text-slate-600">
                  <span className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-emerald-500" />
                    Font Baseline Displacement
                  </span>
                  <span className="font-bold text-slate-800 font-mono">&lt; 1.2px</span>
                </div>
                <div className="flex items-center justify-between text-slate-600">
                  <span className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-emerald-500" />
                    Raster Sharpness Uniformity
                  </span>
                  <span className="font-bold text-slate-800 font-mono">Normal</span>
                </div>
                <div className="flex items-center justify-between text-slate-600">
                  <span className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-slate-400" />
                    MobileNetV3 Region Scan
                  </span>
                  <span className="font-bold text-slate-800 font-mono">Ready (m10)</span>
                </div>
              </div>
            </div>
          </div>

          {/* Settlement & Verification Timeline */}
          <div className="p-6 rounded-xl bg-white border border-slate-200 shadow-subtle flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold text-sm text-slate-900">Verification Pipeline Stage</h3>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 font-bold">
                  ACTIVE
                </span>
              </div>

              <div className="space-y-3 py-1">
                {[
                  { step: '1. SHA-256 Immutable Storage', status: 'Completed', time: '09:21' },
                  { step: '2. PyMuPDF + PaddleOCR', status: 'Completed', time: '09:22' },
                  { step: '3. Decimal Reconciliation', status: 'Completed', time: '09:23' },
                  { step: '4. Sovereign Reviewer Session', status: 'In Progress', time: 'Now' },
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between text-xs">
                    <div className="flex items-center space-x-2">
                      <span className={`w-2 h-2 rounded-full ${idx === 3 ? 'bg-indigo-600 animate-subtle-pulse' : 'bg-emerald-500'}`} />
                      <span className={`font-medium ${idx === 3 ? 'text-indigo-900 font-bold' : 'text-slate-700'}`}>
                        {item.step}
                      </span>
                    </div>
                    <span className="text-[11px] text-slate-400 font-mono">{item.time}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
              <span className="text-slate-500">Active Packet:</span>
              <span className="font-bold text-slate-900">{activeCase?.reference_number}</span>
            </div>
          </div>
        </div>

        {/* RECENT CASE PACKETS TABLE */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-subtle overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Submitted Investigation Packets</h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Review loan dossiers, candidate transactions, and cryptographic verification statuses.
              </p>
            </div>
            <button
              onClick={onNewCase}
              className="text-xs font-semibold text-indigo-600 hover:text-indigo-700"
            >
              + Create Case
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-400 uppercase tracking-wider text-[10px] font-semibold border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3">Reference</th>
                  <th className="px-6 py-3">Applicant Name</th>
                  <th className="px-6 py-3">Files</th>
                  <th className="px-6 py-3">Reconciliation Status</th>
                  <th className="px-6 py-3">Integrity Chain</th>
                  <th className="px-6 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {cases.map((c) => {
                  const isActive = activeCase?.id === c.id;
                  return (
                    <tr
                      key={c.id}
                      className={`hover:bg-slate-50/80 transition-colors cursor-pointer ${
                        isActive ? 'bg-indigo-50/30 font-medium' : ''
                      }`}
                      onClick={() => onSelectCase(c.id)}
                    >
                      <td className="px-6 py-3.5 font-mono font-semibold text-slate-900">
                        {c.reference_number}
                      </td>
                      <td className="px-6 py-3.5 font-medium text-slate-800">
                        {c.applicant_name}
                      </td>
                      <td className="px-6 py-3.5 text-slate-500">
                        {c.documents?.length || 4} PDFs
                      </td>
                      <td className="px-6 py-3.5">
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-red-50 text-red-700 border border-red-200">
                          <AlertCircle className="w-2.5 h-2.5" />
                          2 Discrepancies
                        </span>
                      </td>
                      <td className="px-6 py-3.5 font-mono text-[11px] text-emerald-700">
                        Verified ✓
                      </td>
                      <td className="px-6 py-3.5 text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectCase(c.id);
                            onOpenWorkspace();
                          }}
                          className="px-3 py-1 rounded bg-indigo-50 text-indigo-700 hover:bg-indigo-100 font-semibold text-[11px] transition-colors"
                        >
                          Inspect
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
