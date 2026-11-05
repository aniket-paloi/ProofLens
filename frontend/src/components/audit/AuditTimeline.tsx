import React, { useState } from 'react';
import { AuditEvent } from '../../types';
import { ShieldCheck, AlertTriangle, RefreshCw } from 'lucide-react';

interface AuditTimelineProps {
  events: AuditEvent[];
  onVerify: () => Promise<{ chain_valid: boolean; message: string; total_events: number }>;
}

export const AuditTimeline: React.FC<AuditTimelineProps> = ({ events, onVerify }) => {
  const [verifying, setVerifying] = useState(false);
  const [verificationResult, setVerificationResult] = useState<{
    chain_valid: boolean;
    message: string;
    total_events: number;
  } | null>(null);

  const handleRunVerification = async () => {
    setVerifying(true);
    try {
      const res = await onVerify();
      setVerificationResult(res);
    } finally {
      setVerifying(false);
    }
  };

  return (
    <div className="w-full max-w-6xl mx-auto px-6 mb-12">
      <div className="flex items-center justify-between mb-3">
        <div>
          <span className="text-[11px] font-bold tracking-widest uppercase text-stoic-muted">
            INTEGRITY TIMELINE & AUDIT TRAIL
          </span>
          <h3 className="text-xl font-bold text-stoic-text">
            Cryptographic History
          </h3>
        </div>

        <button
          onClick={handleRunVerification}
          disabled={verifying}
          className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-full bg-stoic-dark text-white text-xs font-semibold hover:bg-neutral-800 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${verifying ? 'animate-spin' : ''}`} />
          <span>Verify Hash Chain</span>
        </button>
      </div>

      {verificationResult && (
        <div
          className={`p-4 rounded-2xl mb-4 border flex items-center space-x-3 text-xs ${
            verificationResult.chain_valid
              ? 'bg-stoic-sageLight border-stoic-sage text-stoic-sage'
              : 'bg-stoic-roseLight border-stoic-rose text-stoic-rose'
          }`}
        >
          {verificationResult.chain_valid ? (
            <ShieldCheck className="w-5 h-5 flex-shrink-0" />
          ) : (
            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          )}
          <div>
            <div className="font-bold">
              {verificationResult.chain_valid ? 'Audit Chain Validated' : 'Audit Chain Compromised'}
            </div>
            <div>{verificationResult.message} ({verificationResult.total_events} events checked)</div>
          </div>
        </div>
      )}

      <div className="bg-stoic-card border border-stoic-border rounded-3xl p-6 overflow-hidden">
        <div className="space-y-4">
          {events.map((ev) => (
            <div
              key={ev.id}
              className="p-4 rounded-2xl bg-stoic-subtle border border-stoic-border flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs"
            >
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-mono font-bold text-stoic-text">
                    #{ev.sequence_number}
                  </span>
                  <span className="font-bold text-stoic-dark uppercase">
                    {ev.action_type}
                  </span>
                  <span className="text-stoic-muted">by {ev.actor_id}</span>
                </div>
                <div className="text-stoic-muted font-mono text-[11px] mt-1 break-all">
                  Hash: {ev.current_event_hash}
                </div>
              </div>

              <div className="text-right text-[11px] text-stoic-muted font-mono flex-shrink-0">
                {new Date(ev.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
              </div>
            </div>
          ))}

          {events.length === 0 && (
            <div className="text-center py-8 text-xs text-stoic-muted">
              No audit events recorded yet for this case.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

