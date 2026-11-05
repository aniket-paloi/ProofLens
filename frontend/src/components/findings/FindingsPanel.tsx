import React, { useState } from 'react';
import { Finding } from '../../types';


interface FindingsPanelProps {
  findings: Finding[];
  onSelectFinding: (finding: Finding) => void;
  onSubmitReview: (findingId: string, disposition: string, reason: string) => Promise<void>;
}

export const FindingsPanel: React.FC<FindingsPanelProps> = ({
  findings,
  onSelectFinding,
  onSubmitReview,
}) => {
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(findings[0] || null);
  const [sliderVal, setSliderVal] = useState<number>(50);
  const [reviewNote, setReviewNote] = useState<string>('');
  const [submitting, setSubmitting] = useState<boolean>(false);

  const handleReviewAction = async (disposition: string) => {
    if (!selectedFinding) return;
    setSubmitting(true);
    try {
      await onSubmitReview(
        selectedFinding.id,
        disposition,
        reviewNote || `Reviewed with confidence weight ${sliderVal}%`
      );
      setReviewNote('');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="w-full max-w-6xl mx-auto px-6 mb-8">
      <div className="text-[11px] font-bold tracking-widest uppercase text-stoic-muted mb-3">
        EVIDENCE-GROUNDED OBSERVATIONS
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Findings List (Left column) */}
        <div className="lg:col-span-5 space-y-3">
          {findings.map((f, idx) => {
            const isSelected = selectedFinding?.id === f.id;
            const isConfirmed = f.reviewer_disposition === 'CONFIRMED';
            const isDismissed = f.reviewer_disposition === 'DISMISSED';

            return (
              <div
                key={f.id}
                onClick={() => {
                  setSelectedFinding(f);
                  onSelectFinding(f);
                }}
                className={`p-5 rounded-3xl border transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-stoic-card border-stoic-dark shadow-sm ring-1 ring-stoic-dark'
                    : 'bg-stoic-card border-stoic-border hover:border-neutral-400'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[10px] font-bold tracking-wider uppercase text-stoic-muted">
                    FINDING {idx + 1} OF {findings.length}
                  </span>
                  
                  {isConfirmed && (
                    <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-stoic-roseLight text-stoic-rose">
                      CONFIRMED
                    </span>
                  )}
                  {isDismissed && (
                    <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-stoic-sageLight text-stoic-sage">
                      DISMISSED
                    </span>
                  )}
                  {!isConfirmed && !isDismissed && (
                    <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-stoic-terracottaLight text-stoic-terracotta">
                      UNREVIEWED
                    </span>
                  )}
                </div>

                <h3 className="text-base font-bold text-stoic-text mb-1">
                  {f.title}
                </h3>

                <p className="text-xs text-stoic-secondary line-clamp-2 leading-relaxed">
                  {f.summary}
                </p>
              </div>
            );
          })}

          {findings.length === 0 && (
            <div className="p-8 text-center rounded-3xl bg-stoic-card border border-stoic-border text-xs text-stoic-muted">
              No findings generated yet. Trigger processing to examine documents.
            </div>
          )}
        </div>

        {/* Detailed Investigation Card (Right column, styled after Stoic question flow) */}
        <div className="lg:col-span-7">
          {selectedFinding ? (
            <div className="bg-stoic-card border border-stoic-border rounded-3xl p-8 shadow-sm flex flex-col justify-between h-full">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <span className="text-[11px] font-bold tracking-widest uppercase text-stoic-muted">
                    REVIEWER DELIBERATION
                  </span>
                  <div className="text-xs text-stoic-muted font-mono">
                    ID: {selectedFinding.id.slice(0, 8)}...
                  </div>
                </div>

                <h2 className="text-2xl font-bold text-stoic-text tracking-tight mb-2">
                  {selectedFinding.title}
                </h2>

                <p className="text-sm text-stoic-secondary leading-relaxed mb-6">
                  {selectedFinding.summary}
                </p>

                {/* Alternative Explanations Scoped Check */}
                <div className="mb-6 p-4 rounded-2xl bg-stoic-subtle border border-stoic-border">
                  <div className="text-[11px] font-bold uppercase tracking-wider text-stoic-text mb-2">
                    Alternative Explanations Checked:
                  </div>
                  <ul className="text-xs text-stoic-secondary space-y-1 list-disc list-inside">
                    {selectedFinding.alternative_explanations.map((alt, i) => (
                      <li key={i}>{alt}</li>
                    ))}
                  </ul>
                </div>

                {/* Tactile Stoic Slider: Subjective Confidence Assessment */}
                <div className="mb-6">
                  <div className="flex items-center justify-between text-xs text-stoic-secondary mb-2">
                    <span className="font-semibold text-stoic-text">Reviewer Certainty Weight</span>
                    <span>{sliderVal}%</span>
                  </div>

                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={sliderVal}
                    onChange={(e) => setSliderVal(Number(e.target.value))}
                    className="stoic-slider"
                  />

                  <div className="flex justify-between text-[11px] text-stoic-muted mt-1.5 font-medium">
                    <span>Not at all</span>
                    <span>Very confident</span>
                  </div>
                </div>

                {/* Optional Reviewer Reason */}
                <div className="mb-6">
                  <input
                    type="text"
                    value={reviewNote}
                    onChange={(e) => setReviewNote(e.target.value)}
                    placeholder="Add reviewer notes or justification (optional)..."
                    className="w-full text-xs px-4 py-3 rounded-2xl bg-stoic-subtle border border-stoic-border text-stoic-text placeholder-stoic-muted focus:outline-none focus:ring-1 focus:ring-stoic-dark"
                  />
                </div>
              </div>

              {/* Disposition Action Buttons */}
              <div className="flex flex-wrap items-center gap-3 pt-4 border-t border-stoic-border">
                <button
                  disabled={submitting}
                  onClick={() => handleReviewAction('CONFIRMED')}
                  className="px-5 py-2.5 rounded-full text-xs font-semibold bg-stoic-dark text-white hover:bg-neutral-800 transition-colors disabled:opacity-50"
                >
                  Confirm Observation
                </button>

                <button
                  disabled={submitting}
                  onClick={() => handleReviewAction('DISMISSED')}
                  className="px-5 py-2.5 rounded-full text-xs font-semibold bg-stoic-subtle text-stoic-text border border-stoic-border hover:bg-neutral-200 transition-colors disabled:opacity-50"
                >
                  Dismiss (Legitimate Variance)
                </button>

                <button
                  disabled={submitting}
                  onClick={() => handleReviewAction('FURTHER_VERIFICATION_NEEDED')}
                  className="px-5 py-2.5 rounded-full text-xs font-semibold bg-stoic-subtle text-stoic-muted border border-stoic-border hover:text-stoic-text transition-colors disabled:opacity-50"
                >
                  Flag for Issuer Query
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-stoic-card border border-stoic-border rounded-3xl p-12 text-center text-stoic-muted text-sm">
              Select an observation on the left to examine evidence and register reviewer disposition.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

