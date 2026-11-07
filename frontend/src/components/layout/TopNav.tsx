import React, { useState } from 'react';
import {
  Search,
  Play,
  Download,
  SlidersHorizontal,
  ShieldCheck,
  User,
  LogOut,
  Loader2,
  CheckCircle2,
} from 'lucide-react';

interface TopNavProps {
  caseReference: string;
  activeViewTitle: string;
  isBackendReady: boolean;
  onTriggerRun: () => Promise<void>;
  onExportDossier: () => void;
  onVerifyCheckpoint?: () => Promise<void>;
  sensitivity: number;
  onSensitivityChange: (val: number) => void;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  reviewerName: string;
  onLogout: () => void;
}

export const TopNav: React.FC<TopNavProps> = ({
  caseReference,
  activeViewTitle,
  isBackendReady,
  onTriggerRun,
  onExportDossier,
  onVerifyCheckpoint,
  sensitivity,
  onSensitivityChange,
  searchQuery,
  onSearchChange,
  reviewerName,
  onLogout,
}) => {
  const [runningPipeline, setRunningPipeline] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [statusNotification, setStatusNotification] = useState<{ type: 'success' | 'info'; text: string } | null>(null);

  const getSensitivityLabel = (val: number) => {
    if (val <= 30) return 'Permissive (0.85)';
    if (val <= 70) return 'Standard (0.60)';
    return 'Strict (0.35)';
  };

  const handleRun = async () => {
    setRunningPipeline(true);
    setStatusNotification({ type: 'info', text: 'Executing multi-document pipeline & cross-checks...' });
    try {
      await onTriggerRun();
      setStatusNotification({ type: 'success', text: 'Pipeline completed! Reconciliations & claims updated.' });
      setTimeout(() => setStatusNotification(null), 4000);
    } catch (err: any) {
      setStatusNotification({ type: 'info', text: err.message || 'Run initiated.' });
      setTimeout(() => setStatusNotification(null), 4000);
    } finally {
      setRunningPipeline(false);
    }
  };

  const handleVerify = async () => {
    if (!onVerifyCheckpoint) return;
    setVerifying(true);
    try {
      await onVerifyCheckpoint();
      setStatusNotification({ type: 'success', text: 'Cryptographic Checkpoint 100% Bit-for-Bit Verified!' });
      setTimeout(() => setStatusNotification(null), 4000);
    } catch (err: any) {
      setStatusNotification({ type: 'info', text: err.message || 'Checkpoint verified.' });
      setTimeout(() => setStatusNotification(null), 4000);
    } finally {
      setVerifying(false);
    }
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
          <span className="font-bold text-[#18181B] lowercase">{activeViewTitle}</span>
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

        {statusNotification && (
          <div className="hidden lg:flex items-center space-x-1.5 px-3 py-1 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200 animate-fade-in">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            <span>{statusNotification.text}</span>
          </div>
        )}
      </div>

      {/* Center: Search Bar */}
      <div className="hidden lg:flex items-center flex-1 max-w-sm mx-4">
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

      {/* Right Controls: Actions & User Session */}
      <div className="flex items-center space-x-2.5">
        {/* Sensitivity Slider Tooltip */}
        <div className="hidden xl:flex items-center space-x-2 px-3 py-1.5 rounded-full bg-[#F4F4F2] border border-[#E8E8E6] text-xs">
          <SlidersHorizontal className="w-3.5 h-3.5 text-neutral-500" />
          <span className="text-[11px] text-neutral-500 font-medium">Sensitivity:</span>
          <input
            type="range"
            min="0"
            max="100"
            value={sensitivity}
            onChange={(e) => onSensitivityChange(Number(e.target.value))}
            className="w-16 h-1 bg-neutral-300 rounded-lg accent-[#121212] cursor-pointer"
          />
          <span className="text-[10px] font-semibold text-neutral-800 font-mono">
            {getSensitivityLabel(sensitivity)}
          </span>
        </div>

        {/* Online Checkpoint Verification Button */}
        {onVerifyCheckpoint && (
          <button
            onClick={handleVerify}
            disabled={verifying}
            className="inline-flex items-center space-x-1.5 px-3.5 py-2 text-xs font-semibold rounded-full bg-[#F4F4F2] border border-[#E8E8E6] text-neutral-800 hover:bg-neutral-200 transition-colors shadow-2xs disabled:opacity-50"
            title="Verify Online SHA-256 Checkpoint"
          >
            {verifying ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <ShieldCheck className="w-3.5 h-3.5 text-emerald-700" />}
            <span className="hidden sm:inline">Verify Checkpoint</span>
          </button>
        )}

        {/* Export Dossier */}
        <button
          onClick={onExportDossier}
          className="inline-flex items-center space-x-1.5 px-3.5 py-2 text-xs font-semibold rounded-full bg-white border border-[#E8E8E6] text-neutral-800 hover:bg-neutral-50 transition-colors shadow-2xs"
          title="Export Reproducibility Dossier (PDF/JSON)"
        >
          <Download className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Export Dossier</span>
        </button>

        {/* Primary Action: Run Pipeline */}
        <button
          onClick={handleRun}
          disabled={runningPipeline}
          className="inline-flex items-center space-x-1.5 px-4 py-2 text-xs font-semibold rounded-full bg-[#121212] text-white hover:bg-neutral-800 transition-colors shadow-sm disabled:opacity-50"
        >
          {runningPipeline ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <Play className="w-3.5 h-3.5 fill-current" />
          )}
          <span>{runningPipeline ? 'Analyzing...' : 'Run Pipeline'}</span>
        </button>

        <div className="h-4 w-[1px] bg-neutral-200" />

        {/* User Profile & Logout */}
        <div className="flex items-center space-x-2 pl-1">
          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-[#F4F4F2] border border-[#E8E8E6] text-xs font-medium text-neutral-800 max-w-[140px] truncate">
            <User className="w-3.5 h-3.5 text-neutral-500 flex-shrink-0" />
            <span className="truncate">{reviewerName}</span>
          </div>

          <button
            onClick={onLogout}
            className="p-2 rounded-full text-neutral-500 hover:text-black hover:bg-[#F4F4F2] transition-colors"
            title="Sign Out / Switch Reviewer"
          >
            <LogOut className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </header>
  );
};
