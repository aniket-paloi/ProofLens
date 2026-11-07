import React, { useState } from 'react';
import { Edit3 } from 'lucide-react';

export const CoverageView: React.FC = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [correctedValue, setCorrectedValue] = useState('₹ 75,000.00');
  const [correctionReason, setCorrectionReason] = useState('Corrected OCR currency symbol misread on line 4');

  const checkMatrix = [
    { id: 'CHK_NET_SALARY_MATCH', name: 'Net Salary Reconciliation', lifecycle: 'COMPLETED', applicability: 'APPLICABLE', outcome: 'POSSIBLE_EXPLANATION', details: 'Split payroll explains variance' },
    { id: 'CHK_PDF_STREAM_SYNC', name: 'Native vs. Rendered Text Cross-Check', lifecycle: 'COMPLETED', applicability: 'APPLICABLE', outcome: 'CONSISTENT', details: 'Stream and visible OCR matched within 1.1px' },
    { id: 'CHK_EMPLOYER_MATCH', name: 'Employer Legal Name Matching', lifecycle: 'COMPLETED', applicability: 'APPLICABLE', outcome: 'CONSISTENT', details: 'APEX FIN TECH LABS PVT verified' },
    { id: 'CHK_RUNNING_BALANCE', name: 'Bank Running Balance Integrity', lifecycle: 'COMPLETED', applicability: 'APPLICABLE', outcome: 'CONSISTENT', details: 'Consecutive transactions reconciled' },
    { id: 'CHK_FONT_BASELINE', name: 'Font Baseline & Saliency Analysis', lifecycle: 'COMPLETED', applicability: 'APPLICABLE', outcome: 'CONSISTENT', details: 'Normal baseline tolerance 0.42px' },
    { id: 'CHK_SIGNATURE_AUTH', name: 'Biometric Signature Authentication', lifecycle: 'NOT_STARTED', applicability: 'UNSUPPORTED', outcome: 'UNABLE_TO_ASSESS', details: 'Requires biometric specimen reference' },
    { id: 'CHK_EXT_BANK_API', name: 'Live Direct Core-Banking Hook', lifecycle: 'NOT_STARTED', applicability: 'UNSUPPORTED', outcome: 'UNABLE_TO_ASSESS', details: 'Offline sovereign demo mode' },
  ];

  return (
    <div className="flex-1 overflow-y-auto p-8 bg-[#FBFBF9] text-[#18181B] font-sans">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-600" />
            <span className="text-[11px] font-bold tracking-widest uppercase text-neutral-500">
              PROMPT 11 & 13 • COVERAGE MATRIX & CORRECTION PROPAGATION
            </span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-[#18181B] mt-1">
            coverage & corrections.
          </h1>
          <p className="text-xs text-neutral-600 mt-1 max-w-2xl leading-relaxed">
            Separates lifecycle states (completed/failed), applicability (applicable/unsupported), and outcomes 
            (consistent/discrepancy/insufficient evidence). Reviewer corrections create immutable versioned revisions.
          </p>
        </div>

        {/* Coverage Matrix Table */}
        <div className="bg-white border border-[#E8E8E6] rounded-3xl p-6 shadow-2xs">
          <div className="flex items-center justify-between mb-4">
            <span className="text-[11px] font-bold tracking-widest uppercase text-neutral-400">
              AUDITED CHECK COVERAGE (7 CHECKS EVALUATED)
            </span>
            <span className="text-xs font-mono text-neutral-500">Coverage: 5/5 Applicable Executed</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[#E8E8E6] text-neutral-500 uppercase tracking-wider text-[11px]">
                  <th className="py-2.5 px-3">Check Identifier</th>
                  <th className="py-2.5 px-3">Description</th>
                  <th className="py-2.5 px-3">Lifecycle</th>
                  <th className="py-2.5 px-3">Applicability</th>
                  <th className="py-2.5 px-3">Outcome</th>
                  <th className="py-2.5 px-3">Evidence Notes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E8E8E6]">
                {checkMatrix.map(c => (
                  <tr key={c.id}>
                    <td className="py-3 px-3 font-mono font-bold text-neutral-800">{c.id}</td>
                    <td className="py-3 px-3 font-medium text-neutral-900">{c.name}</td>
                    <td className="py-3 px-3">
                      <span className="text-[10px] px-2.5 py-0.5 rounded-full font-bold bg-[#F4F4F2] text-neutral-700">
                        {c.lifecycle}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <span className={`text-[10px] px-2.5 py-0.5 rounded-full font-bold ${
                        c.applicability === 'APPLICABLE' ? 'bg-neutral-100 text-neutral-800' : 'bg-neutral-200 text-neutral-500'
                      }`}>
                        {c.applicability}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <span className={`text-[10px] px-2.5 py-0.5 rounded-full font-bold ${
                        c.outcome === 'CONSISTENT' ? 'bg-emerald-100 text-emerald-800' :
                        c.outcome === 'POSSIBLE_EXPLANATION' ? 'bg-amber-100 text-amber-800' :
                        'bg-neutral-100 text-neutral-500'
                      }`}>
                        {c.outcome}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-neutral-600">{c.details}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Inline Field Revision & Correction Propagation Box */}
        <div className="bg-white border border-[#E8E8E6] rounded-3xl p-6 shadow-2xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <span className="text-[11px] font-bold tracking-widest uppercase text-neutral-400">
                PROMPT 13 • IMMUTABLE FIELD REVISION
              </span>
              <h3 className="text-lg font-bold text-[#18181B] mt-0.5">
                Reviewer Field Correction & Dependency Propagation
              </h3>
            </div>
            <button
              onClick={() => setIsEditing(!isEditing)}
              className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-full bg-[#121212] text-white text-xs font-semibold hover:bg-neutral-800"
            >
              <Edit3 className="w-3.5 h-3.5" />
              <span>{isEditing ? 'Close Editor' : 'Edit Extracted Value'}</span>
            </button>
          </div>

          <p className="text-xs text-neutral-600 leading-relaxed mb-4">
            When a reviewer corrects an ambiguous extraction, an immutable <code className="font-mono bg-neutral-100 px-1 py-0.5 rounded">FieldRevision</code> row is 
            created. The original raw extraction is preserved, while dependent financial checks recalculate with a new audit event.
          </p>

          {isEditing ? (
            <div className="p-6 rounded-2xl bg-[#F4F4F2] border border-[#E8E8E6] space-y-4">
              <div>
                <label className="block text-xs font-bold text-[#18181B] mb-1">
                  Corrected Value for Field: <span className="font-mono">salary_slip_m1.net_salary</span>
                </label>
                <input
                  type="text"
                  value={correctedValue}
                  onChange={(e) => setCorrectedValue(e.target.value)}
                  className="w-full text-xs px-4 py-3 rounded-2xl bg-white border border-[#E8E8E6] text-[#18181B] font-mono focus:outline-none focus:ring-1 focus:ring-black"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-[#18181B] mb-1">
                  Reviewer Reason (Mandatory for Audit Log)
                </label>
                <input
                  type="text"
                  value={correctionReason}
                  onChange={(e) => setCorrectionReason(e.target.value)}
                  className="w-full text-xs px-4 py-3 rounded-2xl bg-white border border-[#E8E8E6] text-[#18181B] focus:outline-none focus:ring-1 focus:ring-black"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  onClick={() => setIsEditing(false)}
                  className="px-4 py-2 rounded-full text-xs font-semibold bg-white border border-[#E8E8E6] text-neutral-600 hover:text-black"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    alert(`Applied FieldRevision: ${correctedValue} with reason "${correctionReason}". Dependent checks recomputed.`);
                    setIsEditing(false);
                  }}
                  className="px-5 py-2 rounded-full text-xs font-semibold bg-[#121212] text-white hover:bg-neutral-800 shadow-sm"
                >
                  Save Revision & Recompute
                </button>
              </div>
            </div>
          ) : (
            <div className="p-4 rounded-2xl bg-[#F4F4F2] font-mono text-xs flex items-center justify-between text-neutral-700">
              <div>
                <span className="text-neutral-400">Current Value:</span> <span className="font-bold text-[#18181B]">{correctedValue}</span>
                <span className="text-neutral-400 ml-4">Revision:</span> <span className="font-bold text-neutral-800">#2</span>
              </div>
              <span className="text-emerald-700 font-sans font-semibold">✓ Propagated to Reconciliation Engine</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
