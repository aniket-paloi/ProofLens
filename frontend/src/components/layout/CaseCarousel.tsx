import React from 'react';
import { Case } from '../../types';
import { Plus } from 'lucide-react';

interface CaseCarouselProps {
  cases: Case[];
  activeCaseId: string | null;
  onSelectCase: (caseId: string) => void;
  onNewCase: () => void;
}

export const CaseCarousel: React.FC<CaseCarouselProps> = ({
  cases,
  activeCaseId,
  onSelectCase,
  onNewCase,
}) => {
  return (
    <div className="w-full max-w-6xl mx-auto px-6 my-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-[11px] font-bold tracking-widest uppercase text-stoic-muted">
          ACTIVE LOAN PACKETS
        </span>
        <button
          onClick={onNewCase}
          className="text-xs font-medium text-stoic-dark hover:underline flex items-center space-x-1"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>New Case</span>
        </button>
      </div>

      <div className="flex items-center space-x-3 overflow-x-auto pb-2 scrollbar-none">
        {cases.map((c) => {
          const isActive = c.id === activeCaseId;
          return (
            <button
              key={c.id}
              onClick={() => onSelectCase(c.id)}
              className={`flex-shrink-0 px-4 py-3 rounded-2xl transition-all duration-150 text-left border ${
                isActive
                  ? 'bg-stoic-card border-stoic-dark shadow-sm ring-1 ring-stoic-dark'
                  : 'bg-stoic-subtle border-stoic-border hover:border-neutral-400'
              }`}
            >
              <div className="text-[10px] uppercase font-bold tracking-wider text-stoic-muted">
                {c.reference_number}
              </div>
              <div className="text-sm font-semibold text-stoic-text mt-0.5 whitespace-nowrap">
                {c.applicant_name}
              </div>
            </button>
          );
        })}

        {cases.length === 0 && (
          <div className="text-xs text-stoic-muted py-2 italic">
            No active investigation cases. Click "New Case" to begin.
          </div>
        )}
      </div>
    </div>
  );
};

