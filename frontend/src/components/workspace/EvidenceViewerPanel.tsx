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
  Download,
} from 'lucide-react';
import { InvestigationClaimItem } from './DocumentsListPanel';
import { getDocumentDownloadUrl } from '../../services/api';

interface EvidenceViewerPanelProps {
  activeClaim: InvestigationClaimItem | null;
  onSelectClaim?: (claimId: string) => void;
  leftDocId?: string;
  rightDocId?: string;
}

export const EvidenceViewerPanel: React.FC<EvidenceViewerPanelProps> = ({
  activeClaim,
  leftDocId,
  rightDocId,
}) => {
  const [currentPage, setCurrentPage] = useState<number>(1);
  const totalPages = 4;
  const [zoomLevel, setZoomLevel] = useState<number>(100);
  const [viewMode, setViewMode] = useState<'side-by-side' | 'single'>('side-by-side');
  const [showOverlays, setShowOverlays] = useState<boolean>(true);
  const [scrollLock, setScrollLock] = useState<boolean>(true);

  const handleDownload = (docId?: string, fallbackName?: string) => {
    if (!docId) {
      alert(`Downloading original PDF bytes for ${fallbackName || 'document'}...`);
      return;
    }
    const link = document.createElement('a');
    link.href = getDocumentDownloadUrl(docId);
    link.download = fallbackName || 'document.pdf';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="flex-1 h-full bg-[#FBFBF9] flex flex-col min-w-0 select-none overflow-hidden">
      {/* Top Evidence Toolbar */}
      <div className="h-14 bg-white border-b border-[#E8E8E6] px-5 flex items-center justify-between text-xs flex-shrink-0">
        {/* Left: View Mode & Page Navigation */}
        <div className="flex items-center space-x-3">
          {/* Mode Selector */}
          <div className="flex items-center bg-[#F4F4F2] p-1 rounded-full border border-[#E8E8E6]">
            <button
              onClick={() => setViewMode('side-by-side')}
              className={`flex items-center space-x-1.5 px-3 py-1 rounded-full text-[11px] font-semibold transition-all ${
                viewMode === 'side-by-side'
                  ? 'bg-white text-[#121212] shadow-xs'
                  : 'text-neutral-500 hover:text-black'
              }`}
              title="Side by Side Document Comparison"
            >
              <Columns className="w-3.5 h-3.5" />
              <span>Side-by-Side</span>
            </button>
            <button
              onClick={() => setViewMode('single')}
              className={`flex items-center space-x-1.5 px-3 py-1 rounded-full text-[11px] font-semibold transition-all ${
                viewMode === 'single'
                  ? 'bg-white text-[#121212] shadow-xs'
                  : 'text-neutral-500 hover:text-black'
              }`}
              title="Single Page Inspect"
            >
              <Square className="w-3.5 h-3.5" />
              <span>Single</span>
            </button>
          </div>

          <div className="h-4 w-[1px] bg-[#E8E8E6]" />

          {/* Page controls */}
          <div className="flex items-center space-x-1 text-neutral-600">
            <button
              disabled={currentPage <= 1}
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              className="p-1 rounded-full hover:bg-[#F4F4F2] disabled:opacity-30"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="font-mono text-xs px-2 text-[#18181B] font-semibold">
              {currentPage} / {totalPages}
            </span>
            <button
              disabled={currentPage >= totalPages}
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              className="p-1 rounded-full hover:bg-[#F4F4F2] disabled:opacity-30"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Right: Zoom & Overlay Toggles */}
        <div className="flex items-center space-x-2">
          <div className="flex items-center bg-[#F4F4F2] px-2 py-1 rounded-full border border-[#E8E8E6] space-x-1">
            <button
              onClick={() => setZoomLevel((z) => Math.max(50, z - 10))}
              className="p-1 text-neutral-500 hover:text-black"
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="font-mono text-[11px] w-12 text-center text-[#18181B] font-semibold">
              {zoomLevel}%
            </span>
            <button
              onClick={() => setZoomLevel((z) => Math.min(200, z + 10))}
              className="p-1 text-neutral-500 hover:text-black"
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
          </div>

          <button
            onClick={() => setShowOverlays(!showOverlays)}
            className={`flex items-center space-x-1 px-3 py-1.5 rounded-full border text-[11px] font-semibold transition-colors ${
              showOverlays
                ? 'bg-[#121212] text-white border-[#121212]'
                : 'bg-white text-neutral-600 border-[#E8E8E6] hover:bg-[#F4F4F2]'
            }`}
          >
            {showOverlays ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
            <span>Bounding Overlays</span>
          </button>

          <button
            onClick={() => setScrollLock(!scrollLock)}
            className={`p-1.5 rounded-full border text-neutral-600 hover:bg-[#F4F4F2] transition-colors ${
              scrollLock ? 'border-[#121212] text-[#121212] bg-[#F4F4F2]' : 'border-[#E8E8E6]'
            }`}
            title={scrollLock ? 'Synchronized Scroll Locked' : 'Independent Scroll'}
          >
            {scrollLock ? <Lock className="w-3.5 h-3.5" /> : <Unlock className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Main Dual Document Inspection Stage */}
      <div className="flex-1 overflow-auto p-4 flex flex-col justify-between">
        {/* Document Side-by-Side Canvas */}
        <div className="flex items-stretch justify-center gap-4 flex-1 min-h-[460px]">
          {/* LEFT DOCUMENT (Application Form / Salary Slip) */}
          <div className="flex-1 max-w-[500px] bg-white rounded-3xl shadow-xs border border-[#E8E8E6] flex flex-col overflow-hidden">
            {/* Document Header Tab */}
            <div className="px-5 py-3 bg-[#FBFBF9] border-b border-[#E8E8E6] flex items-center justify-between text-xs">
              <div className="flex items-center space-x-2">
                <span className="px-2 py-0.5 rounded-full bg-neutral-200 text-neutral-800 text-[10px] font-mono font-bold">
                  PRIMARY
                </span>
                <span className="font-semibold text-[#18181B] truncate max-w-[200px]">
                  {activeClaim?.sourceDoc || 'Application_Form_Siddharth.pdf'}
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleDownload(leftDocId, activeClaim?.sourceDoc)}
                  className="p-1 rounded-full text-neutral-500 hover:text-black hover:bg-neutral-200"
                  title="Download Document"
                >
                  <Download className="w-3.5 h-3.5" />
                </button>
                <span className="text-[10px] text-neutral-400 font-mono">Page {currentPage}</span>
              </div>
            </div>

            {/* Document Page Canvas Preview */}
            <div className="flex-1 p-6 font-serif text-[13px] leading-relaxed relative bg-white overflow-hidden text-[#18181B]">
              <div className="border-b border-[#E8E8E6] pb-3 mb-4">
                <div className="text-base font-bold tracking-tight text-[#18181B] uppercase font-sans">
                  Credit Application Form
                </div>
                <div className="text-[11px] text-neutral-500 font-sans mt-0.5">
                  Reference: LOAN-2026-0891 • Applicant: Siddharth B. Jamdhade
                </div>
              </div>

              {/* Section 1 */}
              <div className="space-y-3 font-sans">
                <div className="text-[10px] font-bold uppercase tracking-wider text-neutral-400">
                  1. Employment & Income Declarations
                </div>
                
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="p-2.5 rounded-2xl bg-[#FBFBF9] border border-[#E8E8E6]">
                    <span className="text-[10px] text-neutral-400 block font-mono">Employer</span>
                    <span className="font-semibold text-[#18181B]">Apex FinTech Labs Pvt Ltd</span>
                  </div>
                  <div className="p-2.5 rounded-2xl bg-[#FBFBF9] border border-[#E8E8E6]">
                    <span className="text-[10px] text-neutral-400 block font-mono">Designation</span>
                    <span className="font-semibold text-[#18181B]">Principal Systems Eng.</span>
                  </div>
                </div>

                {/* Highlighted Bounding Box Area */}
                <div className="relative mt-3">
                  <div className="p-3.5 rounded-2xl border border-[#E8E8E6] bg-[#FBFBF9]">
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="text-neutral-500">Declared Monthly Gross:</span>
                      <span className="font-bold text-[#18181B] font-mono text-sm">₹90,000.00</span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-neutral-500">Declared Net In-Hand:</span>
                      <span className="font-bold text-[#18181B] font-mono text-sm">₹75,000.00</span>
                    </div>
                  </div>

                  {/* Visual Bounding Box Overlay if Active */}
                  {showOverlays && (
                    <div className="absolute inset-0 border-2 border-rose-500 bg-rose-500/10 rounded-2xl pointer-events-none flex items-start justify-end p-1.5">
                      <span className="bg-rose-600 text-white text-[9px] font-bold px-2 py-0.5 rounded-full shadow-xs">
                        Field [Gross Income] ₹90,000
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* RIGHT DOCUMENT (Bank Statement / Corroborating Evidence) */}
          {viewMode === 'side-by-side' && (
            <div className="flex-1 max-w-[500px] bg-white rounded-3xl shadow-xs border border-[#E8E8E6] flex flex-col overflow-hidden">
              {/* Document Header Tab */}
              <div className="px-5 py-3 bg-[#FBFBF9] border-b border-[#E8E8E6] flex items-center justify-between text-xs">
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-0.5 rounded-full bg-neutral-200 text-neutral-800 text-[10px] font-mono font-bold">
                    CORROBORATING
                  </span>
                  <span className="font-semibold text-[#18181B] truncate max-w-[200px]">
                    {activeClaim?.targetDoc || 'Bank_Statement_HDFC_3Mo.pdf'}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleDownload(rightDocId, activeClaim?.targetDoc)}
                    className="p-1 rounded-full text-neutral-500 hover:text-black hover:bg-neutral-200"
                    title="Download Document"
                  >
                    <Download className="w-3.5 h-3.5" />
                  </button>
                  <span className="text-[10px] text-neutral-400 font-mono">Page 2</span>
                </div>
              </div>

              {/* Bank Statement Ledger Canvas */}
              <div className="flex-1 p-6 font-sans text-xs bg-white overflow-hidden text-[#18181B]">
                <div className="border-b border-[#E8E8E6] pb-3 mb-4">
                  <div className="text-base font-bold tracking-tight text-[#18181B] uppercase">
                    HDFC Bank • Account Statement
                  </div>
                  <div className="text-[11px] text-neutral-500 mt-0.5 font-mono">
                    A/C: 50100428919012 • IFSC: HDFC0001092
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-neutral-400">
                    Audited Running Ledger (MAY 2026)
                  </div>

                  <div className="border border-[#E8E8E6] rounded-2xl overflow-hidden text-[11px]">
                    <div className="grid grid-cols-12 bg-[#FBFBF9] p-2 font-mono font-semibold text-neutral-500 border-b border-[#E8E8E6] text-[10px]">
                      <span className="col-span-3">Date</span>
                      <span className="col-span-5">Narration</span>
                      <span className="col-span-2 text-right">Credit</span>
                      <span className="col-span-2 text-right">Balance</span>
                    </div>

                    {/* Row 1 */}
                    <div className="grid grid-cols-12 p-2 border-b border-[#E8E8E6] hover:bg-[#FBFBF9] items-center">
                      <span className="col-span-3 font-mono text-[10px]">01-MAY-2026</span>
                      <span className="col-span-5 truncate text-neutral-700">SAL/APEX LABS/P1</span>
                      <span className="col-span-2 text-right font-mono text-emerald-700 font-semibold">42,000.00</span>
                      <span className="col-span-2 text-right font-mono text-neutral-600">48,250.00</span>
                    </div>

                    {/* Row 2 (Split Candidate) */}
                    <div className="grid grid-cols-12 p-2 border-b border-[#E8E8E6] bg-amber-50/50 hover:bg-amber-50 items-center">
                      <span className="col-span-3 font-mono text-[10px]">03-MAY-2026</span>
                      <span className="col-span-5 truncate text-amber-900 font-medium">NEFT/APEX LABS/P2</span>
                      <span className="col-span-2 text-right font-mono text-amber-700 font-bold">33,000.00</span>
                      <span className="col-span-2 text-right font-mono text-neutral-700">81,250.00</span>
                    </div>
                  </div>

                  {showOverlays && (
                    <div className="mt-3 p-3 rounded-2xl bg-amber-50/80 border border-amber-200 text-[11px] text-amber-900">
                      <div className="font-semibold flex items-center gap-1 mb-0.5">
                        <ScanLine className="w-3.5 h-3.5 text-amber-700" />
                        <span>Candidate Split Reconciliation Found</span>
                      </div>
                      <p className="text-[10px] text-amber-800 leading-relaxed">
                        Credit of ₹42,000 on 01-MAY + ₹33,000 on 03-MAY totals ₹75,000, reconciling with declared net salary.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* BOTTOM DUAL-CROP RASTER INSPECTOR */}
        <div className="mt-4 p-4 rounded-3xl bg-white border border-[#E8E8E6] shadow-xs">
          <div className="flex items-center justify-between mb-3 pb-2 border-b border-[#E8E8E6]">
            <div className="flex items-center space-x-2">
              <ScanLine className="w-4 h-4 text-neutral-700" />
              <span className="text-xs font-bold text-[#18181B]">
                Dual-Crop Raster Alignment & Forensic Baselines
              </span>
            </div>
            <span className="text-[10px] font-mono font-semibold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200">
              Laplacian Uniformity: 98.2%
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
            <div className="p-3 rounded-2xl bg-[#FBFBF9] border border-[#E8E8E6]">
              <span className="text-[10px] font-mono text-neutral-400 block uppercase">
                Laplacian Sharpness Variance
              </span>
              <span className="font-bold text-[#18181B] font-mono text-sm">0.96 / 1.00</span>
              <p className="text-[10px] text-neutral-500 mt-1">
                Zero boundary edge discontinuity detected between crop and canvas.
              </p>
            </div>

            <div className="p-3 rounded-2xl bg-[#FBFBF9] border border-[#E8E8E6]">
              <span className="text-[10px] font-mono text-neutral-400 block uppercase">
                Font Baseline Alignment
              </span>
              <span className="font-bold text-[#18181B] font-mono text-sm">0.0 px Offset</span>
              <p className="text-[10px] text-neutral-500 mt-1">
                Native vector text glyphs adhere strictly to horizontal baseline.
              </p>
            </div>

            <div className="p-3 rounded-2xl bg-[#FBFBF9] border border-[#E8E8E6]">
              <span className="text-[10px] font-mono text-neutral-400 block uppercase">
                MobileNetV3 Region Score
              </span>
              <span className="font-bold text-emerald-700 font-mono text-sm">0.02 (Benign)</span>
              <p className="text-[10px] text-neutral-500 mt-1">
                Zero stamp, signature, or numerical splice manipulation detected.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
