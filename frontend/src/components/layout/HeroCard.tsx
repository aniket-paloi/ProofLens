import React from 'react';
import { ArrowRight, Sparkles } from 'lucide-react';

interface HeroCardProps {
  applicantName: string;
  referenceNumber: string;
  documentCount: number;
  findingCount: number;
  onBeginReview: () => void;
}

export const HeroCard: React.FC<HeroCardProps> = ({
  applicantName,
  referenceNumber,
  documentCount,
  findingCount,
  onBeginReview,
}) => {
  return (
    <div className="w-full max-w-6xl mx-auto px-6 mb-6">
      <div className="bg-stoic-dark text-white rounded-3xl p-8 relative overflow-hidden shadow-sm">
        {/* Subtle decorative background glow */}
        <div className="absolute -right-16 -top-16 w-64 h-64 rounded-full bg-neutral-800/40 blur-3xl pointer-events-none" />

        <div className="max-w-xl relative z-10">
          <div className="text-[11px] font-bold tracking-widest uppercase text-neutral-400 mb-2 flex items-center space-x-1.5">
            <Sparkles className="w-3.5 h-3.5 text-neutral-300" />
            <span>CASE OVERVIEW • {referenceNumber}</span>
          </div>

          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-white mb-2">
            {applicantName}
          </h2>

          <p className="text-sm text-neutral-300 leading-relaxed mb-6">
            Reviewing submitted loan packet ({documentCount} documents). 
            Extracted financial claims, visual observations, and transaction flows are cross-examined against typed boundaries.
          </p>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={onBeginReview}
              className="inline-flex items-center space-x-2 bg-white text-stoic-dark font-semibold text-sm px-6 py-3 rounded-full hover:bg-neutral-100 transition-colors"
            >
              <span>Inspect Evidence</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <div className="px-4 py-2.5 rounded-full bg-neutral-900 border border-neutral-700 text-xs text-neutral-300">
              <span className="font-semibold text-white">{findingCount}</span> Observations to inspect
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

