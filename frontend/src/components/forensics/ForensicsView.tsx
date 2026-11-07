import React, { useState } from 'react';
export const ForensicsView: React.FC = () => {
  const [selectedDetector, setSelectedDetector] = useState<'stream_sync' | 'sharpness' | 'mobilenet'>('stream_sync');

  return (
    <div className="flex-1 overflow-y-auto p-8 bg-[#FBFBF9] text-[#18181B] font-sans">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-600" />
            <span className="text-[11px] font-bold tracking-widest uppercase text-neutral-500">
              PROMPT 07, 09, 10, 11 • MULTI-LAYER FORENSICS & VISION BASELINE
            </span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-[#18181B] mt-1">
            visual & layer forensics.
          </h1>
          <p className="text-xs text-neutral-600 mt-1 max-w-2xl leading-relaxed">
            Multi-modal forensic analysis examining underlying PDF operator streams, independent pixel re-OCR, 
            local sharpness variance, font baselines, and Torchvision MobileNetV3 Small region classifier scores.
          </p>
        </div>

        {/* Tab Selector */}
        <div className="flex items-center space-x-2 border-b border-[#E8E8E6] pb-3">
          <button
            onClick={() => setSelectedDetector('stream_sync')}
            className={`px-4 py-2 rounded-full text-xs font-semibold transition-all ${
              selectedDetector === 'stream_sync'
                ? 'bg-[#121212] text-white'
                : 'bg-white border border-[#E8E8E6] text-neutral-600 hover:text-black'
            }`}
          >
            PDF Stream vs. Raster Cross-Check (Prompt 07)
          </button>
          <button
            onClick={() => setSelectedDetector('sharpness')}
            className={`px-4 py-2 rounded-full text-xs font-semibold transition-all ${
              selectedDetector === 'sharpness'
                ? 'bg-[#121212] text-white'
                : 'bg-white border border-[#E8E8E6] text-neutral-600 hover:text-black'
            }`}
          >
            Laplacian Sharpness & Font Baseline (Prompt 09)
          </button>
          <button
            onClick={() => setSelectedDetector('mobilenet')}
            className={`px-4 py-2 rounded-full text-xs font-semibold transition-all ${
              selectedDetector === 'mobilenet'
                ? 'bg-[#121212] text-white'
                : 'bg-white border border-[#E8E8E6] text-neutral-600 hover:text-black'
            }`}
          >
            MobileNetV3 Small Region Classifier (Prompt 10-11)
          </button>
        </div>

        {/* Content based on tab */}
        {selectedDetector === 'stream_sync' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-6 rounded-3xl bg-white border border-[#E8E8E6] shadow-2xs">
                <div className="text-[11px] font-bold text-neutral-400 uppercase tracking-wider mb-2">
                  LAYER 1 • NATIVE PDF VECTOR STREAM
                </div>
                <div className="p-4 rounded-2xl bg-[#F4F4F2] font-mono text-xs text-neutral-800 space-y-1">
                  <div>/Type /Page /Contents 4 0 R</div>
                  <div>BT /F1 12.0 Tf 72 712 Td (Net Salary: 75,000 INR) Tj ET</div>
                  <div className="text-emerald-700 font-bold">✓ Native Text: "75,000 INR" (Render Opacity: 1.0)</div>
                </div>
                <div className="text-xs text-neutral-500 mt-3">
                  Directly parsed using PyMuPDF vector span stream extraction.
                </div>
              </div>

              <div className="p-6 rounded-3xl bg-white border border-[#E8E8E6] shadow-2xs">
                <div className="text-[11px] font-bold text-neutral-400 uppercase tracking-wider mb-2">
                  LAYER 2 • INDEPENDENT RASTER OCR OF VISIBLE PIXELS
                </div>
                <div className="p-4 rounded-2xl bg-[#F4F4F2] font-mono text-xs text-neutral-800 space-y-1">
                  <div>Image Render: 150 DPI RGB [595x842]</div>
                  <div>Region Crop: [ymin: 0.25, xmin: 0.40, ymax: 0.28, xmax: 0.65]</div>
                  <div className="text-emerald-700 font-bold">✓ OCR Readout: "75,000 INR" (Confidence: 0.992)</div>
                </div>
                <div className="text-xs text-neutral-500 mt-3">
                  Rendered page independently raster-OCRed to ensure no hidden invisible layers exist.
                </div>
              </div>
            </div>

            <div className="p-6 rounded-3xl bg-[#121212] text-white shadow-sm flex items-center justify-between">
              <div>
                <div className="text-[11px] font-bold tracking-widest uppercase text-emerald-400">
                  STREAM-TO-PIXEL ALIGNMENT VERIFIED
                </div>
                <h3 className="text-xl font-bold mt-0.5">Discrepancy Score: 0.00% (No Ghost Layers Detected)</h3>
                <p className="text-xs text-neutral-300 mt-1 max-w-xl">
                  Selectable text matches visible pixels within 1.1px spatial tolerance. 
                  Zero white-on-white text prompt injections or OCR drift detected in the submitted packet.
                </p>
              </div>
              <span className="px-4 py-2 rounded-full bg-emerald-950/80 text-emerald-300 border border-emerald-800 text-xs font-bold font-mono">
                CLEAN LAYER
              </span>
            </div>
          </div>
        )}

        {selectedDetector === 'sharpness' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-6 rounded-3xl bg-white border border-[#E8E8E6] shadow-2xs">
                <div className="text-[11px] font-bold text-neutral-400 uppercase">Laplacian Sharpness Variance</div>
                <div className="text-2xl font-black text-[#18181B] mt-1 font-mono">412.8 σ²</div>
                <div className="text-xs text-emerald-700 font-medium mt-1">Uniform across page regions (Clean)</div>
              </div>

              <div className="p-6 rounded-3xl bg-white border border-[#E8E8E6] shadow-2xs">
                <div className="text-[11px] font-bold text-neutral-400 uppercase">Font Baseline Displacement</div>
                <div className="text-2xl font-black text-[#18181B] mt-1 font-mono">0.42 px</div>
                <div className="text-xs text-emerald-700 font-medium mt-1">Within expected printing tolerance (&lt;1.5px)</div>
              </div>

              <div className="p-6 rounded-3xl bg-white border border-[#E8E8E6] shadow-2xs">
                <div className="text-[11px] font-bold text-neutral-400 uppercase">Contrast Discontinuity Ratio</div>
                <div className="text-2xl font-black text-[#18181B] mt-1 font-mono">1.03x</div>
                <div className="text-xs text-emerald-700 font-medium mt-1">No localized digital paste halo detected</div>
              </div>
            </div>

            <div className="p-6 rounded-3xl bg-white border border-[#E8E8E6] shadow-2xs">
              <h3 className="text-base font-bold text-[#18181B] mb-2">Native Font Family & Baseline Consistency</h3>
              <p className="text-xs text-neutral-600 leading-relaxed mb-4">
                Inspection of embedded font subsets across Application Form, Salary Slips, and Bank Statement.
              </p>
              <div className="p-4 rounded-2xl bg-[#F4F4F2] font-mono text-xs text-neutral-800 space-y-1">
                <div>• Font 1: Helvetica-Bold (Embedded Subset, Encoding: WinAnsiEncoding)</div>
                <div>• Font 2: Helvetica (Embedded Subset, Encoding: WinAnsiEncoding)</div>
                <div>• Baseline variance across 42 key-value cells: Max 0.8px, Mean 0.22px (Normal)</div>
              </div>
            </div>
          </div>
        )}

        {selectedDetector === 'mobilenet' && (
          <div className="space-y-6">
            <div className="p-6 rounded-3xl bg-white border border-[#E8E8E6] shadow-2xs">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <span className="text-[11px] font-bold tracking-widest uppercase text-neutral-400">
                    MODEL CARD & EVALUATION RUNTIME
                  </span>
                  <h3 className="text-lg font-bold text-[#18181B] mt-0.5">
                    Torchvision MobileNetV3 Small (Region-Level Saliency Classifier)
                  </h3>
                </div>
                <span className="px-3 py-1 rounded-full bg-neutral-100 text-neutral-800 text-xs font-mono font-bold">
                  Weights: mobilenet_v3_small_region.pt (6.2 MB)
                </span>
              </div>

              <p className="text-xs text-neutral-600 leading-relaxed mb-6">
                Evaluates proposed 224x224px contextual crops around numerical amounts and date fields. 
                Trained on synthetic loan documents with matched degradations. Scores candidate regions without 
                hallucinating pixel segmentation masks.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 rounded-2xl bg-[#F4F4F2] border border-[#E8E8E6]">
                  <div className="text-[11px] font-bold text-neutral-500 uppercase">Crop: Gross Salary Field</div>
                  <div className="text-xl font-bold text-[#18181B] mt-1 font-mono">Score: 0.082</div>
                  <div className="text-xs text-emerald-700 mt-1 font-semibold">Classification: Authentic Region</div>
                </div>

                <div className="p-4 rounded-2xl bg-[#F4F4F2] border border-[#E8E8E6]">
                  <div className="text-[11px] font-bold text-neutral-500 uppercase">Crop: Net Salary Field</div>
                  <div className="text-xl font-bold text-[#18181B] mt-1 font-mono">Score: 0.094</div>
                  <div className="text-xs text-emerald-700 mt-1 font-semibold">Classification: Authentic Region</div>
                </div>

                <div className="p-4 rounded-2xl bg-[#F4F4F2] border border-[#E8E8E6]">
                  <div className="text-[11px] font-bold text-neutral-500 uppercase">Crop: Bank Balance Ledger</div>
                  <div className="text-xl font-bold text-[#18181B] mt-1 font-mono">Score: 0.115</div>
                  <div className="text-xs text-emerald-700 mt-1 font-semibold">Classification: Authentic Region</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
