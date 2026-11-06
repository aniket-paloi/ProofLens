import React, { useState } from 'react';
import { AuditEvent } from '../../types';
import { ShieldCheck, AlertTriangle, RefreshCw, Hash } from 'lucide-react';

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
    <div className="flex-1 h-[calc(100vh-4rem)] overflow-y-auto p-8 bg-slate-50 select-none">
      <div className="max-w-5xl mx-auto space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 text-xs font-semibold text-indigo-600 mb-1">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-subtle-pulse" />
              <span className="uppercase tracking-wider">Cryptographic Proof & Event Trail</span>
            </div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              Append-Only Audit Hash Chain
            </h1>
            <p className="text-xs text-slate-500 mt-1">
              Every ingestion, OCR extraction, and reviewer action is cryptographically chained via canonical JSON SHA-256 hashes.
            </p>
          </div>

          <button
            onClick={handleRunVerification}
            disabled={verifying}
            className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-indigo-600 text-white text-xs font-semibold hover:bg-indigo-700 transition-colors shadow-sm disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${verifying ? 'animate-spin' : ''}`} />
            <span>Verify Offline Checkpoint</span>
          </button>
        </div>

        {verificationResult && (
          <div
            className={`p-4 rounded-xl border flex items-center space-x-3 text-xs shadow-subtle ${
              verificationResult.chain_valid
                ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
                : 'bg-red-50 border-red-200 text-red-800'
            }`}
          >
            {verificationResult.chain_valid ? (
              <ShieldCheck className="w-5 h-5 flex-shrink-0 text-emerald-600" />
            ) : (
              <AlertTriangle className="w-5 h-5 flex-shrink-0 text-red-600" />
            )}
            <div>
              <div className="font-bold">
                {verificationResult.chain_valid ? 'Cryptographic Chain Validated' : 'Audit Chain Compromised'}
              </div>
              <div className="text-[11px] mt-0.5">{verificationResult.message} ({verificationResult.total_events} events checked)</div>
            </div>
          </div>
        )}

        {/* Audit Events List */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-subtle p-6">
          <div className="space-y-3">
            {events.map((ev) => (
              <div
                key={ev.id}
                className="p-3.5 rounded-lg bg-slate-50 border border-slate-200/90 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs"
              >
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono font-bold text-slate-900 bg-white border border-slate-200 px-1.5 py-0.5 rounded text-[10px]">
                      #{ev.sequence_number}
                    </span>
                    <span className="font-bold text-indigo-900 uppercase tracking-wider text-[11px]">
                      {ev.action_type}
                    </span>
                    <span className="text-slate-400 text-[11px]">by {ev.actor_id}</span>
                  </div>
                  <div className="text-slate-500 font-mono text-[10px] break-all flex items-center gap-1">
                    <Hash className="w-3 h-3 text-slate-400 flex-shrink-0" />
                    <span>{ev.current_event_hash}</span>
                  </div>
                </div>

                <div className="text-right text-[11px] text-slate-400 font-mono flex-shrink-0">
                  {new Date(ev.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                </div>
              </div>
            ))}

            {events.length === 0 && (
              <div className="p-8 text-center text-xs text-slate-400">
                No audit events recorded yet for this packet.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
