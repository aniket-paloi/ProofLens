import React from 'react';
import { CheckCircle2 } from 'lucide-react';

export const ReconciliationView: React.FC = () => {

  return (
    <div className="flex-1 overflow-y-auto p-8 bg-[#FBFBF9] text-[#18181B] font-sans">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-emerald-600" />
              <span className="text-[11px] font-bold tracking-widest uppercase text-neutral-500">
                PROMPT 08 • DETERMINISTIC FINANCIAL RECONCILIATION
              </span>
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight text-[#18181B] mt-1">
              financial reconciliation.
            </h1>
            <p className="text-xs text-neutral-600 mt-1 max-w-2xl leading-relaxed">
              Aligns typed financial claims across application declarations, 3 salary slips, and covering bank statements.
              Calculates candidate employer payroll matches with split-payment detection and running balance tracking using Python <code className="font-mono bg-neutral-200 px-1 py-0.5 rounded">Decimal</code>.
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold px-3 py-1.5 rounded-full bg-white border border-[#E8E8E6] shadow-2xs font-mono">
              Precision: Decimal(14,2)
            </span>
          </div>
        </div>

        {/* 3 Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-6 rounded-3xl bg-white border border-[#E8E8E6] shadow-2xs">
            <div className="text-[11px] font-bold tracking-wider uppercase text-neutral-400 mb-1">
              DECLARED GROSS INCOME
            </div>
            <div className="text-2xl font-black text-[#18181B]">₹90,000.00</div>
            <div className="text-xs text-neutral-500 mt-1">From Application Form • Monthly Gross</div>
          </div>

          <div className="p-6 rounded-3xl bg-white border border-[#E8E8E6] shadow-2xs">
            <div className="text-[11px] font-bold tracking-wider uppercase text-neutral-400 mb-1">
              NET PAYSLIP SALARY
            </div>
            <div className="text-2xl font-black text-[#18181B]">₹75,000.00</div>
            <div className="text-xs text-neutral-500 mt-1">Salary Slip M1 • Deductions ₹15,000 (PF, Tax)</div>
          </div>

          <div className="p-6 rounded-3xl bg-[#121212] text-white rounded-3xl p-6 shadow-sm">
            <div className="text-[11px] font-bold tracking-wider uppercase text-neutral-400 mb-1">
              RECONCILED BANK CREDITS
            </div>
            <div className="text-2xl font-black text-white">₹75,000.00</div>
            <div className="text-xs text-emerald-400 mt-1 font-semibold flex items-center space-x-1">
              <CheckCircle2 className="w-3.5 h-3.5 inline" />
              <span>100% Reconciled via Split Payroll</span>
            </div>
          </div>
        </div>

        {/* Legitimate Alternative Check Box: Split Payment Resolution */}
        <div className="p-6 rounded-3xl bg-white border border-[#E8E8E6] shadow-2xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <span className="text-[11px] font-bold tracking-widest uppercase text-neutral-400">
                ALTERNATIVE EXPLANATION EVALUATION
              </span>
              <h3 className="text-lg font-bold text-[#18181B] mt-0.5">
                Resolution of Apparent Discrepancy (Split Payroll Transfer)
              </h3>
            </div>
            <span className="text-xs font-bold px-3 py-1 rounded-full bg-emerald-100 text-emerald-900 border border-emerald-200">
              LEGISLATIVELY RESOLVED
            </span>
          </div>

          <p className="text-xs text-neutral-600 leading-relaxed mb-6">
            A naive verification system would flag a ₹48,000 discrepancy between declared gross (₹90k) and initial bank credit (₹42k).
            ProofLens's financial intelligence identified statutory deductions (₹15k) and discovered a secondary corporate transfer of ₹33,000 two days later from the same corporate entity account.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-2xl bg-[#F4F4F2] border border-[#E8E8E6]">
              <div className="text-[11px] font-bold text-neutral-500 uppercase">Primary Credit (01-MAY)</div>
              <div className="text-lg font-bold text-[#18181B] mt-1">₹42,000.00</div>
              <div className="text-[11px] text-neutral-500 font-mono mt-0.5">TXN #88291 • CMS/APEX LABS</div>
            </div>

            <div className="p-4 rounded-2xl bg-[#F4F4F2] border border-[#E8E8E6]">
              <div className="text-[11px] font-bold text-neutral-500 uppercase">Secondary Credit (03-MAY)</div>
              <div className="text-lg font-bold text-[#18181B] mt-1">₹33,000.00</div>
              <div className="text-[11px] text-neutral-500 font-mono mt-0.5">TXN #88340 • NEFT/APEX DISB</div>
            </div>

            <div className="p-4 rounded-2xl bg-white border border-emerald-500/40">
              <div className="text-[11px] font-bold text-emerald-700 uppercase">Reconciled Net Pay</div>
              <div className="text-lg font-bold text-emerald-900 mt-1">₹75,000.00</div>
              <div className="text-[11px] text-emerald-700 font-medium mt-0.5">Exact Match to Net Salary Slip</div>
            </div>
          </div>
        </div>

        {/* Bank Statement Running Balance Table */}
        <div className="bg-white border border-[#E8E8E6] rounded-3xl p-6 shadow-2xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <span className="text-[11px] font-bold tracking-widest uppercase text-neutral-400">
                AUDITED LEDGER
              </span>
              <h3 className="text-lg font-bold text-[#18181B] mt-0.5">
                Bank Statement Transaction Running Balance Audit
              </h3>
            </div>
            <span className="text-xs text-neutral-500 font-mono">HDFC Bank A/C ••4920</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[#E8E8E6] text-neutral-500 uppercase tracking-wider text-[11px]">
                  <th className="py-2.5 px-3">Date</th>
                  <th className="py-2.5 px-3">Narration</th>
                  <th className="py-2.5 px-3">Type</th>
                  <th className="py-2.5 px-3 text-right">Amount (INR)</th>
                  <th className="py-2.5 px-3 text-right">Running Balance (INR)</th>
                  <th className="py-2.5 px-3 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E8E8E6] font-mono">
                <tr>
                  <td className="py-3 px-3 text-neutral-600">28-APR-2026</td>
                  <td className="py-3 px-3 text-neutral-800 font-sans">Opening Balance B/F</td>
                  <td className="py-3 px-3 text-neutral-500">-</td>
                  <td className="py-3 px-3 text-right text-neutral-500">-</td>
                  <td className="py-3 px-3 text-right font-bold text-neutral-900">₹1,12,450.00</td>
                  <td className="py-3 px-3 text-center font-sans"><span className="text-[10px] px-2 py-0.5 rounded-full bg-neutral-100 text-neutral-700">BASELINE</span></td>
                </tr>
                <tr className="bg-emerald-50/40">
                  <td className="py-3 px-3 text-neutral-600">01-MAY-2026</td>
                  <td className="py-3 px-3 text-neutral-900 font-sans font-medium">CMS/APEX LABS/SALARY-APR26</td>
                  <td className="py-3 px-3 text-emerald-700 font-bold">CREDIT</td>
                  <td className="py-3 px-3 text-right font-bold text-emerald-700">+₹42,000.00</td>
                  <td className="py-3 px-3 text-right font-bold text-neutral-900">₹1,54,450.00</td>
                  <td className="py-3 px-3 text-center font-sans"><span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold">SALARY PART 1</span></td>
                </tr>
                <tr className="bg-emerald-50/40">
                  <td className="py-3 px-3 text-neutral-600">03-MAY-2026</td>
                  <td className="py-3 px-3 text-neutral-900 font-sans font-medium">NEFT/APEX FIN TECH/DISB-REM</td>
                  <td className="py-3 px-3 text-emerald-700 font-bold">CREDIT</td>
                  <td className="py-3 px-3 text-right font-bold text-emerald-700">+₹33,000.00</td>
                  <td className="py-3 px-3 text-right font-bold text-neutral-900">₹1,87,450.00</td>
                  <td className="py-3 px-3 text-center font-sans"><span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold">SALARY PART 2</span></td>
                </tr>
                <tr>
                  <td className="py-3 px-3 text-neutral-600">05-MAY-2026</td>
                  <td className="py-3 px-3 text-neutral-800 font-sans">ACH/MORTGAGE LOAN EMI</td>
                  <td className="py-3 px-3 text-neutral-600">DEBIT</td>
                  <td className="py-3 px-3 text-right text-neutral-800">-₹28,500.00</td>
                  <td className="py-3 px-3 text-right font-bold text-neutral-900">₹1,58,950.00</td>
                  <td className="py-3 px-3 text-center font-sans"><span className="text-[10px] px-2 py-0.5 rounded-full bg-neutral-100 text-neutral-600">VERIFIED</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
