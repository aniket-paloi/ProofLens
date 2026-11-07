import React from 'react';
export const AnalyticsView: React.FC = () => {
  return (
    <div className="flex-1 overflow-y-auto p-8 bg-[#FBFBF9] text-[#18181B] font-sans">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-600" />
            <span className="text-[11px] font-bold tracking-widest uppercase text-neutral-500">
              PROMPT 22 • DESCRIPTIVE REVIEWER FEEDBACK ANALYTICS
            </span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-[#18181B] mt-1">
            reviewer analytics.
          </h1>
          <p className="text-xs text-neutral-600 mt-1 max-w-2xl leading-relaxed">
            Aggregates human reviewer dispositions across investigated loan packets. 
            Operates as descriptive quality analytics without performing unverified online model retraining.
          </p>
        </div>

        {/* 3 Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-6 rounded-3xl bg-white border border-[#E8E8E6] shadow-2xs">
            <div className="text-[11px] font-bold text-neutral-400 uppercase tracking-wider mb-1">
              DISCREPANCIES CONFIRMED
            </div>
            <div className="text-3xl font-black text-rose-700">14</div>
            <div className="text-xs text-neutral-500 mt-1">Confirmed factual inconsistencies</div>
          </div>

          <div className="p-6 rounded-3xl bg-white border border-[#E8E8E6] shadow-2xs">
            <div className="text-[11px] font-bold text-neutral-400 uppercase tracking-wider mb-1">
              LEGITIMATE EXPLANATIONS ACCEPTED
            </div>
            <div className="text-3xl font-black text-emerald-700">38</div>
            <div className="text-xs text-neutral-500 mt-1">Split payroll, tax spread, month shifts</div>
          </div>

          <div className="p-6 rounded-3xl bg-white border border-[#E8E8E6] shadow-2xs">
            <div className="text-[11px] font-bold text-neutral-400 uppercase tracking-wider mb-1">
              FLAGGED FOR ISSUER INQUIRY
            </div>
            <div className="text-3xl font-black text-amber-700">7</div>
            <div className="text-xs text-neutral-500 mt-1">Awaiting secondary payroll documentation</div>
          </div>
        </div>

        {/* Common Categories breakdown */}
        <div className="p-6 rounded-3xl bg-white border border-[#E8E8E6] shadow-2xs">
          <h3 className="text-base font-bold text-[#18181B] mb-4">Top Legitimate Resolution Reasons</h3>
          <div className="space-y-3">
            {[
              { label: 'Split Payroll Disbursement (Multi-day deposits from employer)', count: '24 cases', pct: '63%' },
              { label: 'Gross to Net Statutory Tax/PF Spread', count: '10 cases', pct: '26%' },
              { label: 'Corporate Entity Legal Name Variation', count: '4 cases', pct: '11%' },
            ].map((item, idx) => (
              <div key={idx} className="p-4 rounded-2xl bg-[#F4F4F2] border border-[#E8E8E6] flex items-center justify-between text-xs">
                <div>
                  <span className="font-bold text-[#18181B]">{item.label}</span>
                </div>
                <div className="flex items-center space-x-3 font-mono">
                  <span className="text-neutral-500">{item.count}</span>
                  <span className="font-bold text-neutral-800">{item.pct}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Governance Disclaimer */}
        <div className="p-6 rounded-3xl bg-[#121212] text-white shadow-sm">
          <div className="text-[11px] font-bold tracking-widest uppercase text-neutral-400 mb-1">
            DATA INTEGRITY & RETRAINING GOVERNANCE
          </div>
          <h3 className="text-base font-bold text-white mb-1">
            Zero Unsupervised Online Model Retraining
          </h3>
          <p className="text-xs text-neutral-300 leading-relaxed">
            Per the Prompt 22 specification, reviewer dismissals are never fed back as automatic training weights. 
            All machine learning model retraining requires explicit data curation, validation against clean negatives, 
            and held-out benchmark evaluation.
          </p>
        </div>
      </div>
    </div>
  );
};
