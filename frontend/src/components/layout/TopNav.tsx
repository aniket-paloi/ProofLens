import React from 'react';
import {
  Search,
  Play,
  Download,
  SlidersHorizontal,
} from 'lucide-react';

interface TopNavProps {
  caseReference: string;
  activeViewTitle: string;
  isBackendReady: boolean;
  onTriggerRun: () => void;
  onExportDossier: () => void;
  sensitivity: number;
  onSensitivityChange: (val: number) => void;
  searchQuery: string;
  onSearchChange: (q: string) => void;
}

export const TopNav: React.FC<TopNavProps> = ({
  caseReference,
  activeViewTitle,
  isBackendReady,
  onTriggerRun,
  onExportDossier,
  sensitivity,
  onSensitivityChange,
  searchQuery,
  onSearchChange,
}) => {
  const getSensitivityLabel = (val: number) => {
    if (val <= 30) return 'Permissive (0.85)';
    if (val <= 70) return 'Standard (0.60)';
    return 'Strict (0.35)';
  };

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between z-20 flex-shrink-0 select-none">
      {/* Left: Breadcrumbs & View Title */}
      <div className="flex items-center space-x-3">
        <div className="flex items-center space-x-1.5 text-xs text-slate-500">
          <span className="hover:text-slate-700 cursor-pointer">Cases</span>
          <span>/</span>
          <span className="font-mono font-medium text-slate-700">{caseReference}</span>
          <span>/</span>
          <span className="font-semibold text-slate-900">{activeViewTitle}</span>
        </div>

        <div className="h-4 w-[1px] bg-slate-200 hidden md:block" />

        {/* Backend health status pill */}
        <div className="hidden md:flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-slate-100 text-slate-600 border border-slate-200">
          <span
            className={`w-2 h-2 rounded-full ${
              isBackendReady ? 'bg-emerald-500 animate-subtle-pulse' : 'bg-amber-500'
            }`}
          />
          <span>{isBackendReady ? 'FastAPI 127.0.0.1:8000' : 'Local Standby'}</span>
        </div>
      </div>

      {/* Center: Search Bar */}
      <div className="hidden lg:flex items-center flex-1 max-w-md mx-6">
        <div className="relative w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search claims, OCR tokens, bank transactions, amounts..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full pl-9 pr-4 py-1.5 text-xs rounded-lg bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
          />
        </div>
      </div>

      {/* Right Controls: Sensitivity Slider & Primary Actions */}
      <div className="flex items-center space-x-3">
        {/* Sensitivity Slider Tooltip */}
        <div className="hidden xl:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-50 border border-slate-200 text-xs">
          <SlidersHorizontal className="w-3.5 h-3.5 text-slate-500" />
          <span className="text-[11px] text-slate-500 font-medium">Sensitivity:</span>
          <input
            type="range"
            min="0"
            max="100"
            value={sensitivity}
            onChange={(e) => onSensitivityChange(Number(e.target.value))}
            className="w-20 h-1.5 bg-slate-200 rounded-lg accent-indigo-600 cursor-pointer"
          />
          <span className="text-[11px] font-semibold text-slate-700 font-mono w-24">
            {getSensitivityLabel(sensitivity)}
          </span>
        </div>

        {/* Secondary: Export Dossier */}
        <button
          onClick={onExportDossier}
          className="inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 transition-colors shadow-sm"
          title="Export Reproducibility Dossier (PDF/JSON)"
        >
          <Download className="w-3.5 h-3.5 text-slate-500" />
          <span className="hidden sm:inline">Export Dossier</span>
        </button>

        {/* Primary CTA: Run Investigation Pipeline */}
        <button
          onClick={onTriggerRun}
          className="inline-flex items-center space-x-1.5 px-4 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 active:bg-indigo-800 transition-all shadow-sm shadow-indigo-600/30"
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          <span>Run Pipeline</span>
        </button>
      </div>
    </header>
  );
};
