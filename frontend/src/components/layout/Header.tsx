import React from 'react';
import { ShieldCheck, User } from 'lucide-react';

interface HeaderProps {
  reviewerName?: string;
  isReady: boolean;
}

export const Header: React.FC<HeaderProps> = ({ reviewerName = "Siddharth", isReady }) => {
  return (
    <header className="w-full max-w-6xl mx-auto pt-8 pb-4 px-6 flex items-center justify-between">
      <div>
        <div className="flex items-center space-x-2">
          <span className="inline-block w-2 h-2 rounded-full bg-stoic-sage animate-pulse" />
          <span className="text-[11px] font-semibold tracking-widest uppercase text-stoic-muted">
            PROOF_LENS WORKSPACE
          </span>
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-stoic-text mt-1">
          meet prooflens.
        </h1>
      </div>

      <div className="flex items-center space-x-3">
        <div className="hidden sm:flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-stoic-subtle border border-stoic-border text-xs text-stoic-secondary">
          <ShieldCheck className={`w-4 h-4 ${isReady ? 'text-stoic-sage' : 'text-stoic-terracotta'}`} />
          <span>{isReady ? 'Local Sovereign Mode' : 'Initializing...'}</span>
        </div>

        <button
          className="w-10 h-10 rounded-full bg-stoic-dark text-white flex items-center justify-center hover:opacity-90 transition-opacity"
          title={`Reviewer: ${reviewerName}`}
        >
          <User className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};

