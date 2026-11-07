import React from 'react';
import { ArrowRight, Search, Scale, Sliders, Lock } from 'lucide-react';

interface LandingPageProps {
  onEnterApp: () => void;
  onOpenLogin: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onEnterApp, onOpenLogin }) => {
  return (
    <div className="min-h-screen bg-[#FBFBF9] text-[#18181B] selection:bg-[#121212] selection:text-white font-sans">
      {/* Top Navigation */}
      <nav className="w-full max-w-6xl mx-auto px-6 py-6 flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-full bg-[#121212] flex items-center justify-center text-white font-black text-sm">
            P
          </div>
          <span className="font-bold text-lg tracking-tight text-[#18181B]">prooflens.</span>
        </div>

        <div className="flex items-center space-x-4">
          <button
            onClick={onOpenLogin}
            className="text-xs font-semibold text-neutral-600 hover:text-[#18181B] transition-colors px-3 py-2"
          >
            Sign In
          </button>
          <button
            onClick={onEnterApp}
            className="px-5 py-2.5 rounded-full bg-[#121212] text-white text-xs font-semibold hover:bg-neutral-800 transition-all shadow-sm"
          >
            Launch Workspace
          </button>
        </div>
      </nav>

      {/* Hero Section (Stoic iOS minimal vector aesthetic) */}
      <main className="w-full max-w-5xl mx-auto px-6 pt-12 pb-20 text-center">
        {/* Subtle pill badge */}
        <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-white border border-[#E8E8E6] shadow-2xs mb-6">
          <span className="w-2 h-2 rounded-full bg-emerald-600 animate-pulse" />
          <span className="text-[11px] font-bold tracking-widest uppercase text-neutral-600">
            SOVEREIGN DOCUMENT INVESTIGATION
          </span>
        </div>

        {/* Minimalist Hero Heading */}
        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-[#18181B] max-w-3xl mx-auto leading-[1.12] mb-5">
          meet prooflens.<br />
          <span className="text-neutral-500 font-medium">your financial evidence companion.</span>
        </h1>

        <p className="text-base sm:text-lg text-neutral-600 max-w-2xl mx-auto leading-relaxed mb-8 font-normal">
          Don't just verify documents with opaque percentages. Investigate source-linked facts, 
          cross-examine claims, check legitimate alternatives, and build a reproducible dossier.
        </p>

        {/* Action CTAs */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3.5 mb-14">
          <button
            onClick={onEnterApp}
            className="w-full sm:w-auto px-8 py-3.5 rounded-full bg-[#121212] text-white font-semibold text-sm hover:bg-neutral-800 transition-all flex items-center justify-center space-x-2 shadow-sm"
          >
            <span>Open Reviewer Workspace</span>
            <ArrowRight className="w-4 h-4" />
          </button>
          <button
            onClick={onOpenLogin}
            className="w-full sm:w-auto px-7 py-3.5 rounded-full bg-white text-[#18181B] font-semibold text-sm border border-[#E8E8E6] hover:bg-neutral-50 transition-all"
          >
            Sign In with Reviewer ID
          </button>
        </div>

        {/* Stoic Stylized Vector Art Card */}
        <div className="relative max-w-3xl mx-auto bg-white border border-[#E8E8E6] rounded-3xl p-8 sm:p-12 shadow-sm text-left overflow-hidden">
          <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center">
            {/* Minimalist Monochrome Emblem */}
            <div className="md:col-span-5 flex justify-center">
              <div className="w-48 h-48 rounded-full bg-[#F4F4F2] flex items-center justify-center relative border border-[#E8E8E6]">
                <svg viewBox="0 0 100 100" className="w-32 h-32 fill-[#121212]">
                  {/* Stylized serene lens/bird emblem */}
                  <path d="M 50 15 C 30 15 15 35 15 55 C 15 75 35 85 50 85 C 65 85 85 75 85 55 C 85 35 70 15 50 15 Z" fill="#121212" />
                  <circle cx="50" cy="50" r="18" fill="#FBFBF9" />
                  <circle cx="50" cy="50" r="9" fill="#121212" />
                  <path d="M 70 70 L 90 90" stroke="#121212" strokeWidth="6" strokeLinecap="round" />
                </svg>
              </div>
            </div>

            {/* Evidence Invariants */}
            <div className="md:col-span-7 space-y-3.5">
              <div className="text-[11px] font-bold tracking-widest uppercase text-neutral-400">
                THE PROOFLENS CODE OF EVIDENCE
              </div>
              <h3 className="text-xl font-bold text-[#18181B]">
                Human Sovereignty Over Automated Black-Boxes
              </h3>
              <p className="text-xs text-neutral-600 leading-relaxed">
                ProofLens rejects automated applicant rejections and unexplained authenticity scores. 
                Every finding links directly to coordinate-mapped source crops, compares compatible claims, 
                and evaluates legitimate alternative explanations like split salary disbursements.
              </p>
              <div className="pt-2 flex flex-wrap gap-2 text-[11px] font-mono text-neutral-600">
                <span className="px-2.5 py-1 rounded-full bg-[#F4F4F2] border border-[#E8E8E6]">PyMuPDF + OpenCV</span>
                <span className="px-2.5 py-1 rounded-full bg-[#F4F4F2] border border-[#E8E8E6]">Python Decimal Math</span>
                <span className="px-2.5 py-1 rounded-full bg-[#F4F4F2] border border-[#E8E8E6]">SHA-256 Audit Chain</span>
              </div>
            </div>
          </div>
        </div>

        {/* Feature Grid: 4 Core Pillars */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-12 text-left">
          <div className="bg-white border border-[#E8E8E6] rounded-3xl p-6 shadow-2xs">
            <div className="w-10 h-10 rounded-2xl bg-[#F4F4F2] flex items-center justify-center text-[#121212] mb-4">
              <Scale className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-[#18181B] mb-1">Typed Claims Engine</h4>
            <p className="text-xs text-neutral-600 leading-relaxed">
              Aligns person, annual/monthly frequency, currency, and gross vs. net basis before calculating cross-document variance.
            </p>
          </div>

          <div className="bg-white border border-[#E8E8E6] rounded-3xl p-6 shadow-2xs">
            <div className="w-10 h-10 rounded-2xl bg-[#F4F4F2] flex items-center justify-center text-[#121212] mb-4">
              <Search className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-[#18181B] mb-1">Visual & Layer Forensics</h4>
            <p className="text-xs text-neutral-600 leading-relaxed">
              Cross-checks selectable text streams against independently rendered raster OCR, font baselines, and sharpness variance.
            </p>
          </div>

          <div className="bg-white border border-[#E8E8E6] rounded-3xl p-6 shadow-2xs">
            <div className="w-10 h-10 rounded-2xl bg-[#F4F4F2] flex items-center justify-center text-[#121212] mb-4">
              <Sliders className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-[#18181B] mb-1">Alternative Checks</h4>
            <p className="text-xs text-neutral-600 leading-relaxed">
              Automatically checks split payments, delayed credits across month boundaries, and OCR ambiguity before flagging anomalies.
            </p>
          </div>

          <div className="bg-white border border-[#E8E8E6] rounded-3xl p-6 shadow-2xs">
            <div className="w-10 h-10 rounded-2xl bg-[#F4F4F2] flex items-center justify-center text-[#121212] mb-4">
              <Lock className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-[#18181B] mb-1">Cryptographic History</h4>
            <p className="text-xs text-neutral-600 leading-relaxed">
              Monotonically increasing SHA-256 hash chains commit all reviewer actions, verified against offline retained checkpoints.
            </p>
          </div>
        </div>

        {/* Bottom Banner */}
        <div className="mt-16 pt-8 border-t border-[#E8E8E6] flex flex-col sm:flex-row items-center justify-between text-xs text-neutral-500">
          <div>ProofLens Enterprise Investigation Workspace • Version 0.3.0</div>
          <div className="mt-2 sm:mt-0 font-medium">Prepared for Aniket Paloi • 2026</div>
        </div>
      </main>
    </div>
  );
};
