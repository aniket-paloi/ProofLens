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
    <header className="h-16 bg-white border-b border-[#E8E8E6] px-6 flex items-center justify-between z-20 flex-shrink-0 select-none">
      {/* Left: Breadcrumbs & View Title */}
      <div className="flex items-center space-x-3">
        <div className="flex items-center space-x-1.5 text-xs text-neutral-500">
          <span className="hover:text-black cursor-pointer font-medium">Cases</span>
          <span>/</span>
          <span className="font-mono font-medium text-neutral-700">{caseReference}</span>
          <span>/</span>
          <span className="font-bold text-[#18181B]">{activeViewTitle}</span>
        </div>

        <div className="h-4 w-[1px] bg-neutral-200 hidden md:block" />

        {/* Backend health status pill */}
        <div className="hidden md:flex items-center space-x-1.5 px-3 py-1 rounded-full text-[11px] font-medium bg-[#F4F4F2] text-neutral-700 border border-[#E8E8E6]">
          <span
            className={`w-2 h-2 rounded-full ${
              isBackendReady ? 'bg-emerald-600 animate-pulse' : 'bg-amber-600'
            }`}
          />
          <span>{isBackendReady ? 'FastAPI 127.0.0.1:8000' : 'Local Standby'}</span>
        </div>
      </div>

      {/* Center: Search Bar */}
      <div className="hidden lg:flex items-center flex-1 max-w-md mx-6">
        <div className="relative w-full">
          <Search className="w-4 h-4 text-neutral-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search claims, OCR tokens, bank transactions, amounts..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs rounded-full bg-[#F4F4F2] border border-[#E8E8E6] text-[#18181B] placeholder-neutral-400 focus:outline-none focus:ring-1 focus:ring-[#121212] transition-all"
          />
        </div>
      </div>

      {/* Right Controls: Sensitivity Slider & Primary Actions */}
      <div className="flex items-center space-x-3">
        {/* Sensitivity Slider Tooltip */}
        <div className="hidden xl:flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-[#F4F4F2] border border-[#E8E8E6] text-xs">
          <SlidersHorizontal className="w-3.5 h-3.5 text-neutral-500" />
          <span className="text-[11px] text-neutral-500 font-medium">Sensitivity:</span>
          <input
            type="range"
            min="0"
            max="100"
            value={sensitivity}
            onChange={(e) => onSensitivityChange(Number(e.target.value))}
            className="w-20 h-1.5 bg-neutral-300 rounded-lg accent-[#121212] cursor-pointer"
          />
          <span className="text-[11px] font-semibold text-neutral-800 font-mono w-24">
            {getSensitivityLabel(sensitivity)}
          </span>
        </div>

        {/* Secondary: Export Dossier */}
        <button
          onClick={onExportDossier}
          className="inline-flex items-center space-x-1.5 px-4 py-2 text-xs font-semibold rounded-full bg-white border border-[#E8E8E6] text-neutral-800 hover:bg-neutral-50 transition-colors shadow-2xs"
          title="Export Reproducibility Dossier (PDF/JSON)"
        >
          <Download className="w-3.5 h-3.5" />
          <span>Dossier</span>
        </button>

        {/* Primary Action: Re-run Investigation */}
        <button
          onClick={onTriggerRun}
          className="inline-flex items-center space-x-1.5 px-4 py-2 text-xs font-semibold rounded-full bg-[#121212] text-white hover:bg-neutral-800 transition-colors shadow-sm"
          title="Run Investigation Pipeline Across All Submitted Documents"
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          <span>Run Pipeline</span>
        </button>
      </div>
    </header>
  );
};
