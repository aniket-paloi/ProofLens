import React, { useState } from 'react';
import {
  ZoomIn,
  ZoomOut,
  Columns,
  Square,
  Lock,
  Unlock,
  Eye,
  EyeOff,
  ChevronLeft,
  ChevronRight,
  ScanLine,
} from 'lucide-react';
import { InvestigationClaimItem } from './DocumentsListPanel';

interface EvidenceViewerPanelProps {
  activeClaim: InvestigationClaimItem | null;
  onSelectClaim?: (claimId: string) => void;
}

export const EvidenceViewerPanel: React.FC<EvidenceViewerPanelProps> = ({
  activeClaim,
}) => {
  const [currentPage, setCurrentPage] = useState<number>(1);
  const totalPages = 4;
  const [zoomLevel, setZoomLevel] = useState<number>(100);
  const [viewMode, setViewMode] = useState<'side-by-side' | 'single'>('side-by-side');
  const [showOverlays, setShowOverlays] = useState<boolean>(true);
  const [scrollLock, setScrollLock] = useState<boolean>(true);
  const showDiffGutter = true;

  return (
    <div className="flex-1 h-full bg-slate-100/70 flex flex-col min-w-0 select-none overflow-hidden">
      {/* Top Evidence Toolbar (Draftable Inspired) */}
      <div className="h-12 bg-white border-b border-slate-200 px-4 flex items-center justify-between text-xs flex-shrink-0">
        {/* Left: View Mode & Page Navigation */}
        <div className="flex items-center space-x-3">
          {/* Mode Selector */}
          <div className="flex items-center bg-slate-100 p-0.5 rounded-lg border border-slate-200">
            <button
              onClick={() => setViewMode('side-by-side')}
              className={`flex items-center space-x-1 px-2.5 py-1 rounded-md text-[11px] font-medium transition-all ${
                viewMode === 'side-by-side'
                  ? 'bg-white text-indigo-700 shadow-sm font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
              title="Side by Side Document Comparison"
            >
              <Columns className="w-3.5 h-3.5" />
              <span>Side-by-Side</span>
            </button>
            <button
              onClick={() => setViewMode('single')}
              className={`flex items-center space-x-1 px-2.5 py-1 rounded-md text-[11px] font-medium transition-all ${
                viewMode === 'single'
                  ? 'bg-white text-indigo-700 shadow-sm font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
              title="Single Page Inspect"
            >
              <Square className="w-3.5 h-3.5" />
              <span>Single</span>
            </button>
          </div>

          <div className="h-4 w-[1px] bg-slate-200" />

          {/* Page controls */}
          <div className="flex items-center space-x-1.5 text-slate-600">
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage <= 1}
              className="p-1 rounded hover:bg-slate-100 disabled:opacity-40"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="font-mono text-slate-800 text-[11px]">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage >= totalPages}
              className="p-1 rounded hover:bg-slate-100 disabled:opacity-40"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Center: Active Highlight Status Pill */}
        {activeClaim && (
          <div className="hidden md:flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-50 border border-slate-200 text-[11px]">
            <span className="w-2 h-2 rounded-full bg-indigo-600 animate-subtle-pulse" />
            <span className="text-slate-500">Inspecting Bounding Box:</span>
            <span className="font-semibold text-slate-800 truncate max-w-[200px]">
              {activeClaim.title}
            </span>
          </div>
        )}

        {/* Right: Overlays, Zoom, and Lock Controls */}
        <div className="flex items-center space-x-2 text-slate-600">
          {/* Overlay Toggle */}
          <button
            onClick={() => setShowOverlays(!showOverlays)}
            className={`p-1.5 rounded-lg border transition-all ${
              showOverlays
                ? 'bg-indigo-50 border-indigo-200 text-indigo-700'
                : 'bg-white border-slate-200 text-slate-500'
            }`}
            title="Toggle Bounding Box Overlays"
          >
            {showOverlays ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
          </button>

          {/* Scroll Lock */}
          <button
            onClick={() => setScrollLock(!scrollLock)}
            className={`p-1.5 rounded-lg border transition-all ${
              scrollLock
                ? 'bg-slate-100 border-slate-300 text-slate-800'
                : 'bg-white border-slate-200 text-slate-400'
            }`}
            title={scrollLock ? 'Synchronized Scroll Locked' : 'Independent Scroll'}
          >
            {scrollLock ? <Lock className="w-4 h-4" /> : <Unlock className="w-4 h-4" />}
          </button>

          {/* Zoom Controls */}
          <div className="flex items-center space-x-1 bg-white border border-slate-200 rounded-lg p-0.5">
            <button
              onClick={() => setZoomLevel(Math.max(50, zoomLevel - 15))}
              className="p-1 hover:bg-slate-100 rounded"
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="font-mono text-[11px] text-slate-700 px-1 w-10 text-center">
              {zoomLevel}%
            </span>
            <button
              onClick={() => setZoomLevel(Math.min(200, zoomLevel + 15))}
              className="p-1 hover:bg-slate-100 rounded"
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Dual Document Inspection Stage */}
      <div className="flex-1 overflow-auto p-4 flex flex-col justify-between">
        {/* Document Side-by-Side Canvas */}
        <div className="flex items-stretch justify-center gap-4 flex-1 min-h-[460px]">
          {/* LEFT DOCUMENT (Application Form / Salary Slip) */}
          <div className="flex-1 max-w-[500px] bg-white rounded-xl shadow-card border border-slate-200/90 flex flex-col overflow-hidden">
            {/* Document Header Tab */}
            <div className="px-4 py-2.5 bg-slate-50/90 border-b border-slate-200 flex items-center justify-between text-xs">
              <div className="flex items-center space-x-2">
                <span className="px-1.5 py-0.5 rounded bg-blue-100 text-blue-800 text-[10px] font-mono font-bold">
                  LEFT
                </span>
                <span className="font-semibold text-slate-800 truncate">
                  Application_Form_Siddharth.pdf
                </span>
              </div>
              <span className="text-[10px] text-slate-400 font-mono">Page 1 • Native PDF</span>
            </div>

            {/* Document Page Canvas Preview */}
            <div className="flex-1 p-6 font-serif text-[13px] leading-relaxed relative bg-white overflow-hidden text-slate-800">
              <div className="border-b-2 border-slate-900 pb-3 mb-4">
                <div className="text-lg font-bold tracking-tight text-slate-900 uppercase font-sans">
                  Credit Application Form
                </div>
                <div className="text-[11px] text-slate-500 font-sans">
                  Reference: LOAN-2026-0891 • Applicant: Siddharth B. Jamdhade
                </div>
              </div>

              {/* Section 1 */}
              <div className="space-y-3 font-sans">
                <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  1. Employment & Income Declarations
                </div>
                
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="p-2 rounded bg-slate-50 border border-slate-100">
                    <span className="text-[10px] text-slate-400 block">Employer</span>
                    <span className="font-semibold text-slate-800">Apex FinTech Labs Pvt Ltd</span>
                  </div>
                  <div className="p-2 rounded bg-slate-50 border border-slate-100">
                    <span className="text-[10px] text-slate-400 block">Designation</span>
                    <span className="font-semibold text-slate-800">Principal Systems Eng.</span>
                  </div>
                </div>

                {/* Highlighted Bounding Box Area */}
                <div className="relative mt-4">
                  <div className="p-3 rounded-lg border border-slate-200 bg-slate-50/50">
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="text-slate-500">Declared Monthly Gross:</span>
                      <span className="font-bold text-slate-900 font-mono text-sm">₹90,000.00</span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-500">Declared Net In-Hand:</span>
                      <span className="font-bold text-slate-900 font-mono text-sm">₹75,000.00</span>
                    </div>
                  </div>

                  {/* Visual Bounding Box Overlay if Active */}
                  {showOverlays && (
                    <div className="absolute inset-0 border-2 border-red-500 bg-red-500/10 rounded-lg pointer-events-none flex items-start justify-end p-1">
                      <span className="bg-red-600 text-white text-[9px] font-bold px-1.5 py-0.5 rounded shadow-sm">
                        Field [Gross Income] ₹90,000
                      </span>
                    </div>
                  )}
                </div>

                <div className="text-[11px] text-slate-500 pt-3 border-t border-slate-100">
                  <p>
                    I hereby declare that all particulars stated above regarding my employment with Apex FinTech Labs are true, complete, and verifiable via corporate bank credits.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* MIDDLE MINIMAP / DIFF GUTTER (Draftable style) */}
          {showDiffGutter && (
            <div className="w-8 bg-white rounded-lg border border-slate-200/80 shadow-subtle flex flex-col items-center justify-between py-3 relative">
              <div className="text-[9px] font-bold text-slate-400 font-mono">DIFF</div>
              <div className="w-2 flex-1 my-2 bg-slate-100 rounded-full relative overflow-hidden">
                <div className="absolute top-[38%] left-0 right-0 h-4 bg-red-500 rounded" title="Discrepancy: Income declared vs statement credit" />
                <div className="absolute top-[52%] left-0 right-0 h-2 bg-amber-400 rounded" title="Candidate: Delayed split credit" />
                <div className="absolute top-[20%] left-0 right-0 h-2 bg-emerald-500 rounded" title="Matched: Employer identity" />
              </div>
              <span className="text-[8px] font-mono text-red-600 font-bold">-48k</span>
            </div>
          )}

          {/* RIGHT DOCUMENT (Bank Statement / Extracted Transaction Ledger) */}
          <div className="flex-1 max-w-[500px] bg-white rounded-xl shadow-card border border-slate-200/90 flex flex-col overflow-hidden">
            {/* Document Header Tab */}
            <div className="px-4 py-2.5 bg-slate-50/90 border-b border-slate-200 flex items-center justify-between text-xs">
              <div className="flex items-center space-x-2">
                <span className="px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 text-[10px] font-mono font-bold">
                  RIGHT
                </span>
                <span className="font-semibold text-slate-800 truncate">
                  Bank_Statement_HDFC_3Mo.pdf
                </span>
              </div>
              <span className="text-[10px] text-slate-400 font-mono">Page 2 • Statement Ledger</span>
            </div>

            {/* Document Page Canvas Preview */}
            <div className="flex-1 p-6 font-sans text-xs leading-relaxed relative bg-white overflow-hidden text-slate-800">
              <div className="border-b border-slate-200 pb-3 mb-3 flex items-center justify-between">
                <div>
                  <div className="font-bold text-slate-900">HDFC BANK SAVINGS ACCOUNT</div>
                  <div className="text-[10px] text-slate-400 font-mono">A/C: *******8821 • IFSC: HDFC0000129</div>
                </div>
                <span className="text-[10px] px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-mono">
                  APR - JUN 2026
                </span>
              </div>

              {/* Transactions Table */}
              <div className="space-y-1.5">
                <div className="grid grid-cols-12 text-[10px] font-bold text-slate-400 uppercase tracking-wider pb-1 border-b border-slate-100">
                  <span className="col-span-3">Date</span>
                  <span className="col-span-5">Narration</span>
                  <span className="col-span-4 text-right">Credit (₹)</span>
                </div>

                {/* Legitimate matched transaction */}
                <div className="grid grid-cols-12 text-[11px] py-1.5 items-center border-b border-slate-50 text-slate-600">
                  <span className="col-span-3 font-mono text-[10px]">28-APR-2026</span>
                  <span className="col-span-5 truncate text-slate-700">UPI/SWIGGY/FOOD</span>
                  <span className="col-span-4 text-right font-mono text-slate-400">-450.00</span>
                </div>

                {/* Primary Discrepancy Transaction with Bounding Overlay */}
                <div className="relative">
                  <div className="grid grid-cols-12 text-[11px] py-2 items-center bg-red-50/60 rounded px-1.5 font-medium text-slate-800">
                    <span className="col-span-3 font-mono text-[10px] text-slate-700">01-MAY-2026</span>
                    <span className="col-span-5 truncate text-slate-900 font-semibold">
                      ACH/SALARY/APEX FIN
                    </span>
                    <span className="col-span-4 text-right font-mono font-bold text-red-600">
                      +42,000.00
                    </span>
                  </div>

                  {showOverlays && (
                    <div className="absolute inset-0 border-2 border-red-500 rounded pointer-events-none flex items-center justify-end pr-2">
                      <span className="bg-red-600 text-white text-[8px] font-bold px-1 rounded shadow-sm">
                        Mismatch: Δ -₹48,000
                      </span>
                    </div>
                  )}
                </div>

                {/* Split candidate transaction 2 days later */}
                <div className="relative mt-1">
                  <div className="grid grid-cols-12 text-[11px] py-2 items-center bg-amber-50/50 rounded px-1.5 font-medium text-slate-800">
                    <span className="col-span-3 font-mono text-[10px] text-slate-700">03-MAY-2026</span>
                    <span className="col-span-5 truncate text-slate-900">
                      NEFT/INCENTIVE/APEX
                    </span>
                    <span className="col-span-4 text-right font-mono font-semibold text-amber-700">
                      +33,000.00
                    </span>
                  </div>

                  {showOverlays && (
                    <div className="absolute inset-0 border border-amber-400 rounded pointer-events-none flex items-center justify-end pr-2">
                      <span className="bg-amber-600 text-white text-[8px] font-bold px-1 rounded">
                        Candidate Split Credit (+2d)
                      </span>
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-12 text-[11px] py-1.5 items-center border-b border-slate-50 text-slate-600">
                  <span className="col-span-3 font-mono text-[10px]">10-MAY-2026</span>
                  <span className="col-span-5 truncate text-slate-700">ATM/WDL/MUMBAI</span>
                  <span className="col-span-4 text-right font-mono text-slate-400">-10,000.00</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* BOTTOM DUAL CROP EVIDENCE COMPARISON BOX */}
        <div className="mt-4 bg-white rounded-xl border border-slate-200 p-3 shadow-card flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-700">
              <ScanLine className="w-4 h-4" />
            </div>
            <div>
              <div className="text-xs font-bold text-slate-900">
                Visual Dual-Crop Alignment & Font Baseline Inspector
              </div>
              <div className="text-[11px] text-slate-500">
                300 DPI high-resolution raster crop comparison between Declaration and Bank Ledger.
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-4 text-xs font-mono">
            <div className="px-3 py-1.5 rounded-lg bg-slate-50 border border-slate-200 flex items-center space-x-2">
              <span className="text-slate-400 text-[10px]">DECLARED CROP:</span>
              <span className="font-bold text-slate-800">₹90,000.00</span>
              <span className="text-[10px] text-emerald-600 font-semibold">12.1pt Arial</span>
            </div>

            <span className="text-slate-400">vs</span>

            <div className="px-3 py-1.5 rounded-lg bg-slate-50 border border-slate-200 flex items-center space-x-2">
              <span className="text-slate-400 text-[10px]">LEDGER CROP:</span>
              <span className="font-bold text-red-600">₹42,000.00</span>
              <span className="text-[10px] text-emerald-600 font-semibold">10.0pt Consolas</span>
            </div>

            <div className="px-2.5 py-1 rounded bg-indigo-50 text-indigo-700 text-[10px] font-semibold border border-indigo-200">
              Discrepancy Confirmed
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
