import React, { useState } from 'react';
import { AuditEvent } from '../../types';
import { ShieldCheck, AlertTriangle, RefreshCw, Hash, Download } from 'lucide-react';

interface AuditTimelineProps {
  events: AuditEvent[];
  onVerify: () => Promise<{ chain_valid: boolean; message: string; total_events: number }>;
  onExportCheckpoint?: () => Promise<any>;
}

export const AuditTimeline: React.FC<AuditTimelineProps> = ({ events, onVerify, onExportCheckpoint }) => {
  const [verifying, setVerifying] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [checkpointModalData, setCheckpointModalData] = useState<any | null>(null);
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

  const handleExport = async () => {
    if (!onExportCheckpoint) return;
    setExporting(true);
    try {
      const data = await onExportCheckpoint();
      setCheckpointModalData(data);
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="flex-1 h-[calc(100vh-4rem)] overflow-y-auto p-8 bg-[#FBFBF9] select-none text-[#18181B]">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header Section */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#E8E8E6]">
          <div>
            <div className="flex items-center space-x-2 text-[11px] font-bold tracking-wider text-neutral-400 uppercase mb-1">
              <span className="w-2 h-2 rounded-full bg-emerald-600" />
              <span>Cryptographic Proof & Immutable Event Ledger</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-[#18181B]">
              cryptographic audit timeline.
            </h1>
            <p className="text-xs text-neutral-500 mt-1">
              Every document ingestion, financial reconciliation, and reviewer action is cryptographically chained via canonical JSON SHA-256 hashes.
            </p>
          </div>

          <div className="flex items-center space-x-2.5">
            {onExportCheckpoint && (
              <button
                onClick={handleExport}
                disabled={exporting}
                className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-full bg-[#F4F4F2] border border-[#E8E8E6] text-neutral-800 text-xs font-semibold hover:bg-neutral-200 transition-colors shadow-2xs disabled:opacity-50"
              >
                <Download className="w-3.5 h-3.5" />
                <span>{exporting ? 'Freezing...' : 'Export Checkpoint'}</span>
              </button>
            )}

            <button
              onClick={handleRunVerification}
              disabled={verifying}
              className="inline-flex items-center space-x-1.5 px-5 py-2 rounded-full bg-[#121212] text-white text-xs font-semibold hover:bg-neutral-800 transition-colors shadow-sm disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${verifying ? 'animate-spin' : ''}`} />
              <span>{verifying ? 'Verifying Chain...' : 'Verify Online Checkpoint'}</span>
            </button>
          </div>
        </div>

        {verificationResult && (
          <div
            className={`p-4 rounded-3xl border flex items-center space-x-3 text-xs shadow-xs ${
              verificationResult.chain_valid
                ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                : 'bg-rose-50 border-rose-200 text-rose-900'
            }`}
          >
            {verificationResult.chain_valid ? (
              <ShieldCheck className="w-5 h-5 flex-shrink-0 text-emerald-700" />
            ) : (
              <AlertTriangle className="w-5 h-5 flex-shrink-0 text-rose-600" />
            )}
            <div>
              <div className="font-bold">
                {verificationResult.chain_valid ? 'Cryptographic Hash Chain 100% Validated' : 'Audit Chain Compromise Detected'}
              </div>
              <div className="text-[11px] mt-0.5 opacity-90">
                {verificationResult.message} ({verificationResult.total_events} sequential events verified against SQLite ledger)
              </div>
            </div>
          </div>
        )}

        {/* Audit Events List Card */}
        <div className="bg-white border border-[#E8E8E6] rounded-3xl shadow-xs p-6">
          <div className="flex items-center justify-between pb-3 mb-4 border-b border-[#E8E8E6]">
            <span className="text-[10px] font-bold uppercase tracking-wider text-neutral-400">
              Chained Events Log ({events.length})
            </span>
            <span className="text-[10px] font-mono text-neutral-400">
              Algorithm: Canonical JSON SHA-256
            </span>
          </div>

          <div className="space-y-3">
            {events.length === 0 ? (
              <div className="p-8 text-center text-xs text-neutral-400">
                No audit events recorded for this case yet.
              </div>
            ) : (
              events.map((ev) => (
                <div
                  key={ev.id}
                  className="p-4 rounded-2xl bg-[#FBFBF9] border border-[#E8E8E6] flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs hover:border-neutral-300 transition-colors"
                >
                  <div className="space-y-1.5">
                    <div className="flex items-center space-x-2">
                      <span className="font-mono font-bold text-[#18181B] bg-white border border-[#E8E8E6] px-2 py-0.5 rounded-full text-[10px]">
                        #{ev.sequence_number}
                      </span>
                      <span className="font-bold text-[#18181B] uppercase tracking-wider text-[11px]">
                        {ev.action_type}
                      </span>
                      <span className="text-neutral-400 text-[11px]">by {ev.actor_id}</span>
                    </div>
                    <div className="text-neutral-500 font-mono text-[10px] break-all flex items-center gap-1">
                      <Hash className="w-3 h-3 text-neutral-400 flex-shrink-0" />
                      <span>{ev.current_event_hash}</span>
                    </div>
                  </div>

                  <div className="text-[10px] font-mono text-neutral-400 whitespace-nowrap self-start sm:self-auto">
                    {new Date(ev.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* RETAINED CHECKPOINT MODAL */}
        {checkpointModalData && (
          <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-white border border-[#E8E8E6] rounded-3xl p-6 max-w-lg w-full shadow-2xl space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-[#E8E8E6]">
                <div className="flex items-center space-x-2">
                  <ShieldCheck className="w-5 h-5 text-emerald-600" />
                  <span className="text-xs font-bold text-[#18181B]">
                    Retained Cryptographic Checkpoint
                  </span>
                </div>
                <button
                  onClick={() => setCheckpointModalData(null)}
                  className="text-neutral-400 hover:text-black text-xs font-bold"
                >
                  Close
                </button>
              </div>

              <div className="space-y-2 text-xs font-mono bg-[#FBFBF9] p-4 rounded-2xl border border-[#E8E8E6]">
                <div className="flex justify-between">
                  <span className="text-neutral-400">Reference:</span>
                  <span className="font-bold">{checkpointModalData.reference_number}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-neutral-400">Events Frozen:</span>
                  <span className="font-bold">{checkpointModalData.event_count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-neutral-400">Status:</span>
                  <span className="font-bold text-emerald-700">{checkpointModalData.verification_status}</span>
                </div>
                <div className="pt-2 border-t border-[#E8E8E6]">
                  <span className="text-[10px] text-neutral-400 block mb-0.5">Chain Digest (SHA-256):</span>
                  <span className="text-[10px] break-all text-neutral-800 font-bold">{checkpointModalData.chain_digest}</span>
                </div>
              </div>

              <div className="flex items-center justify-end">
                <button
                  onClick={() => {
                    const blob = new Blob([JSON.stringify(checkpointModalData, null, 2)], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = checkpointModalData.file_name || 'checkpoint.json';
                    a.click();
                  }}
                  className="px-4 py-2 rounded-full text-xs font-semibold bg-[#121212] text-white hover:bg-neutral-800 flex items-center gap-1.5"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download Frozen Checkpoint JSON</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
