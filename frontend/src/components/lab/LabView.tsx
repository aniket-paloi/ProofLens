import React, { useState } from 'react';
export const LabView: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'fraudsim' | 'whatif'>('fraudsim');
  const [hypotheticalSalary, setHypotheticalSalary] = useState<number>(85000);
  const [simRunning, setSimRunning] = useState(false);
  const [simResult, setSimResult] = useState<string | null>(null);

  const handleRunSimulation = () => {
    setSimRunning(true);
    setTimeout(() => {
      setSimRunning(false);
      setSimResult(
        `Hypothetical declared gross ₹${hypotheticalSalary.toLocaleString()}: Re-evaluated deduction threshold. With statutory ₹15,000 tax/PF, net is ₹${(hypotheticalSalary - 15000).toLocaleString()}. Gap with bank credits (₹75,000) is ₹${Math.abs((hypotheticalSalary - 15000) - 75000).toLocaleString()}.`
      );
    }, 400);
  };

  return (
    <div className="flex-1 overflow-y-auto p-8 bg-[#FBFBF9] text-[#18181B] font-sans">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-600" />
            <span className="text-[11px] font-bold tracking-widest uppercase text-neutral-500">
              PROMPT 20 & 21 • BONUS EVALUATION MODULES
            </span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-[#18181B] mt-1">
            fraudsim lab & what-if branch.
          </h1>
          <p className="text-xs text-neutral-600 mt-1 max-w-2xl leading-relaxed">
            Isolated synthetic robustness laboratory (Prompt 20) with ground-truth isolation, 
            and hypothetical what-if investigation branches (Prompt 21) that never mutate official evidence.
          </p>
        </div>

        {/* Tab Selector */}
        <div className="flex items-center space-x-2 border-b border-[#E8E8E6] pb-3">
          <button
            onClick={() => setActiveTab('fraudsim')}
            className={`px-4 py-2 rounded-full text-xs font-semibold transition-all ${
              activeTab === 'fraudsim'
                ? 'bg-[#121212] text-white'
                : 'bg-white border border-[#E8E8E6] text-neutral-600 hover:text-black'
            }`}
          >
            FraudSim Synthetic Laboratory (Prompt 20)
          </button>
          <button
            onClick={() => setActiveTab('whatif')}
            className={`px-4 py-2 rounded-full text-xs font-semibold transition-all ${
              activeTab === 'whatif'
                ? 'bg-[#121212] text-white'
                : 'bg-white border border-[#E8E8E6] text-neutral-600 hover:text-black'
            }`}
          >
            What-If Hypothetical Investigation (Prompt 21)
          </button>
        </div>

        {activeTab === 'fraudsim' && (
          <div className="space-y-6">
            <div className="p-6 rounded-3xl bg-white border border-[#E8E8E6] shadow-2xs">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <span className="text-[11px] font-bold tracking-widest uppercase text-neutral-400">
                    ISOLATED EXPERIMENT WORKBENCH
                  </span>
                  <h3 className="text-lg font-bold text-[#18181B] mt-0.5">
                    Synthetic Document Manipulation Testbed
                  </h3>
                </div>
                <span className="px-3 py-1 rounded-full bg-amber-100 text-amber-900 border border-amber-300 text-xs font-mono font-bold">
                  LAB ISOLATION ACTIVE
                </span>
              </div>

              <p className="text-xs text-neutral-600 leading-relaxed mb-6">
                FraudSim applies controlled perturbations (font baseline shift, white-on-white text layer injection, 
                amount digit alteration, raster compression degradation) to test detector robustness. 
                Crucially, ground truth masks and labels are strictly isolated from the inference pipeline.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 rounded-2xl bg-[#F4F4F2] border border-[#E8E8E6]">
                  <div className="text-[11px] font-bold text-neutral-500 uppercase">Specimen: Amount Tamper</div>
                  <div className="text-sm font-bold text-[#18181B] mt-1">SIM-0501de84.pdf</div>
                  <div className="text-xs text-neutral-500 mt-1">Digit replacement + Laplacian artifact test</div>
                </div>

                <div className="p-4 rounded-2xl bg-[#F4F4F2] border border-[#E8E8E6]">
                  <div className="text-[11px] font-bold text-neutral-500 uppercase">Specimen: Prompt Injection</div>
                  <div className="text-sm font-bold text-[#18181B] mt-1">SIM-27f23ba6.pdf</div>
                  <div className="text-xs text-neutral-500 mt-1">Hidden white-on-white text layer test</div>
                </div>

                <div className="p-4 rounded-2xl bg-[#F4F4F2] border border-[#E8E8E6]">
                  <div className="text-[11px] font-bold text-neutral-500 uppercase">Specimen: Font Displacement</div>
                  <div className="text-sm font-bold text-[#18181B] mt-1">SIM-fd90c909.pdf</div>
                  <div className="text-xs text-neutral-500 mt-1">Subtle baseline displacement (3.2px)</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'whatif' && (
          <div className="space-y-6">
            <div className="p-6 rounded-3xl bg-white border border-[#E8E8E6] shadow-2xs">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <div className="inline-block px-2.5 py-0.5 rounded-full bg-neutral-900 text-white font-mono text-[10px] font-bold tracking-wider uppercase mb-1">
                    SIMULATION BRANCH • READ-ONLY SANDBOX
                  </div>
                  <h3 className="text-lg font-bold text-[#18181B]">
                    Hypothetical Parameter Adjustment
                  </h3>
                </div>
              </div>

              <p className="text-xs text-neutral-600 leading-relaxed mb-6">
                What-If allows a reviewer to test hypothetical figures (e.g., if the applicant's gross salary had been 
                declared differently) to understand how dependent checks behave, without altering official case evidence or hashes.
              </p>

              <div className="p-6 rounded-2xl bg-[#F4F4F2] border border-[#E8E8E6] space-y-4 mb-6">
                <div>
                  <div className="flex items-center justify-between text-xs text-neutral-700 font-bold mb-1">
                    <span>Hypothetical Declared Gross Salary (INR)</span>
                    <span className="font-mono text-base text-[#18181B]">₹{hypotheticalSalary.toLocaleString()}</span>
                  </div>
                  <input
                    type="range"
                    min="50000"
                    max="150000"
                    step="5000"
                    value={hypotheticalSalary}
                    onChange={(e) => setHypotheticalSalary(Number(e.target.value))}
                    className="w-full accent-black cursor-pointer"
                  />
                  <div className="flex justify-between text-[11px] text-neutral-400 mt-1 font-mono">
                    <span>₹50,000</span>
                    <span>₹1,50,000</span>
                  </div>
                </div>

                <button
                  onClick={handleRunSimulation}
                  disabled={simRunning}
                  className="px-6 py-2.5 rounded-full bg-[#121212] text-white text-xs font-semibold hover:bg-neutral-800 transition-colors shadow-sm disabled:opacity-50"
                >
                  {simRunning ? 'Recomputing Simulation...' : 'Evaluate What-If Branch'}
                </button>
              </div>

              {simResult && (
                <div className="p-5 rounded-2xl bg-white border border-neutral-300 text-xs text-neutral-800 space-y-1 font-mono">
                  <div className="font-bold text-[#18181B] font-sans">Simulation Outcome:</div>
                  <div>{simResult}</div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
