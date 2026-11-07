import React, { useState } from 'react';
export const GraphView: React.FC = () => {
  const [selectedNode, setSelectedNode] = useState<string>('claim-1');

  const nodes = [
    { id: 'doc-app', type: 'DOCUMENT', label: 'Application_Form.pdf', category: 'Source Document' },
    { id: 'doc-slip', type: 'DOCUMENT', label: 'Salary_Slip_M1.pdf', category: 'Source Document' },
    { id: 'doc-bank', type: 'DOCUMENT', label: 'Bank_Statement.pdf', category: 'Source Document' },
    { id: 'claim-1', type: 'CLAIM', label: 'Claim: Monthly Gross = ₹90,000', category: 'Applicant Income Claim' },
    { id: 'claim-2', type: 'CLAIM', label: 'Claim: Net Salary = ₹75,000', category: 'Payslip Declaration' },
    { id: 'txn-1', type: 'TRANSACTION', label: 'Credit: ₹42,000 (01-MAY)', category: 'Primary Payroll Deposit' },
    { id: 'txn-2', type: 'TRANSACTION', label: 'Credit: ₹33,000 (03-MAY)', category: 'Secondary Payroll Deposit' },
    { id: 'alt-1', type: 'ALTERNATIVE', label: 'Legitimate Split Payment', category: 'Verified Explanation' },
  ];

  return (
    <div className="flex-1 overflow-y-auto p-8 bg-[#FBFBF9] text-[#18181B] font-sans">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-600" />
            <span className="text-[11px] font-bold tracking-widest uppercase text-neutral-500">
              PROMPT 14 • CLAIM GRAPH & SOURCE-DEPENDENCY PROVENANCE
            </span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-[#18181B] mt-1">
            claim & evidence graph.
          </h1>
          <p className="text-xs text-neutral-600 mt-1 max-w-2xl leading-relaxed">
            Read projection tracing directional dependencies between source documents, extracted fields, 
            compatible financial claims, bank transactions, and alternative explanations.
          </p>
        </div>

        {/* Graph Visual Canvas Box */}
        <div className="p-8 rounded-3xl bg-white border border-[#E8E8E6] shadow-2xs">
          <div className="text-[11px] font-bold uppercase tracking-wider text-neutral-400 mb-6 flex items-center justify-between">
            <span>DIRECTED DEPENDENCY PROJECTION (PROV-O ALIGNED)</span>
            <span className="px-3 py-1 rounded-full bg-[#F4F4F2] text-neutral-700 text-xs font-mono font-medium">
              8 Active Nodes • 7 Typed Edges
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Level 1: Documents */}
            <div className="space-y-3">
              <div className="text-xs font-bold text-neutral-500 uppercase">1. Sources</div>
              {nodes.filter(n => n.type === 'DOCUMENT').map(node => (
                <div
                  key={node.id}
                  onClick={() => setSelectedNode(node.id)}
                  className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                    selectedNode === node.id
                      ? 'bg-[#121212] text-white border-[#121212] shadow-sm'
                      : 'bg-[#F4F4F2] border-[#E8E8E6] text-neutral-800 hover:border-black'
                  }`}
                >
                  <div className="text-[10px] font-mono text-neutral-400 uppercase">{node.category}</div>
                  <div className="text-xs font-bold mt-1 truncate">{node.label}</div>
                </div>
              ))}
            </div>

            {/* Level 2: Claims & Transactions */}
            <div className="space-y-3">
              <div className="text-xs font-bold text-neutral-500 uppercase">2. Typed Claims & Facts</div>
              {nodes.filter(n => n.type === 'CLAIM' || n.type === 'TRANSACTION').map(node => (
                <div
                  key={node.id}
                  onClick={() => setSelectedNode(node.id)}
                  className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                    selectedNode === node.id
                      ? 'bg-[#121212] text-white border-[#121212] shadow-sm'
                      : 'bg-white border-[#E8E8E6] text-neutral-800 hover:border-black'
                  }`}
                >
                  <div className="text-[10px] font-mono text-neutral-400 uppercase">{node.category}</div>
                  <div className="text-xs font-bold mt-1 truncate">{node.label}</div>
                </div>
              ))}
            </div>

            {/* Level 3: Explanations & Dispositions */}
            <div className="space-y-3">
              <div className="text-xs font-bold text-neutral-500 uppercase">3. Explanations & Reviews</div>
              {nodes.filter(n => n.type === 'ALTERNATIVE').map(node => (
                <div
                  key={node.id}
                  onClick={() => setSelectedNode(node.id)}
                  className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                    selectedNode === node.id
                      ? 'bg-[#121212] text-white border-[#121212] shadow-sm'
                      : 'bg-emerald-50 border-emerald-300 text-emerald-900 hover:border-emerald-600'
                  }`}
                >
                  <div className="text-[10px] font-mono text-emerald-700 uppercase font-bold">{node.category}</div>
                  <div className="text-xs font-bold mt-1">{node.label}</div>
                  <div className="text-[11px] text-emerald-700 mt-2 font-medium">
                    Connects txn-1 (₹42k) + txn-2 (₹33k) to claim-2 (₹75k net)
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Provenance Assurance Box */}
        <div className="p-6 rounded-3xl bg-white border border-[#E8E8E6] shadow-2xs">
          <h3 className="text-sm font-bold text-[#18181B] mb-2">Provenance Independence Categories</h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div className="p-3 rounded-2xl bg-[#F4F4F2] border border-[#E8E8E6]">
              <span className="font-bold text-[#18181B] block mb-1">1. Known Shared Lineage</span>
              <span className="text-neutral-600">Application declared gross derived from employer contract terms.</span>
            </div>
            <div className="p-3 rounded-2xl bg-[#F4F4F2] border border-[#E8E8E6]">
              <span className="font-bold text-[#18181B] block mb-1">2. Independent Acquisition</span>
              <span className="text-neutral-600">Bank statement acquired from HDFC clearing network with verified hash.</span>
            </div>
            <div className="p-3 rounded-2xl bg-[#F4F4F2] border border-[#E8E8E6]">
              <span className="font-bold text-[#18181B] block mb-1">3. Default State</span>
              <span className="text-neutral-600">Unknown independence default prevents false corroboration multipliers.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
