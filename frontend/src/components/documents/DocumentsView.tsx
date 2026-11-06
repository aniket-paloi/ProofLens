import React from 'react';
import { FileText, Upload, CheckCircle2, Hash, ShieldCheck } from 'lucide-react';
import { PacketDocument } from '../workspace/DocumentsListPanel';

interface DocumentsViewProps {
  documents: PacketDocument[];
  onUploadDoc: () => void;
  onOpenWorkspace: () => void;
}

export const DocumentsView: React.FC<DocumentsViewProps> = ({
  documents,
  onUploadDoc,
  onOpenWorkspace,
}) => {
  return (
    <div className="flex-1 h-[calc(100vh-4rem)] overflow-y-auto p-8 bg-slate-50 select-none">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 text-xs font-semibold text-indigo-600 mb-1">
              <span className="w-2 h-2 rounded-full bg-indigo-600 animate-subtle-pulse" />
              <span className="uppercase tracking-wider">Storage & Immutability Guarantee</span>
            </div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              Submitted Document Packets
            </h1>
            <p className="text-xs text-slate-500 mt-1">
              Original bytes stored immutably in storage/originals with SHA-256 hashes. Derivatives maintained in separate pipelines.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={onUploadDoc}
              className="inline-flex items-center space-x-1.5 px-4 py-2 text-xs font-semibold rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm"
            >
              <Upload className="w-3.5 h-3.5" />
              <span>Upload Document</span>
            </button>
          </div>
        </div>

        {/* Documents Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="p-5 rounded-xl bg-white border border-slate-200 shadow-subtle flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2 text-slate-700">
                    <div className="w-8 h-8 rounded-lg bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-700">
                      <FileText className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-slate-900">{doc.name}</div>
                      <span className="text-[10px] uppercase font-mono font-semibold text-slate-400">
                        {doc.type}
                      </span>
                    </div>
                  </div>

                  <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1">
                    <CheckCircle2 className="w-2.5 h-2.5" />
                    PROCESSED
                  </span>
                </div>

                <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 text-[11px] font-mono text-slate-600 space-y-1 mb-4">
                  <div className="flex items-center justify-between text-slate-500">
                    <span>Pages: {doc.pages}</span>
                    <span>Size: {doc.size}</span>
                  </div>
                  <div className="text-[10px] text-slate-400 break-all flex items-center gap-1">
                    <Hash className="w-3 h-3 flex-shrink-0" />
                    <span>{doc.checksum}</span>
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                <span className="text-[11px] text-emerald-700 flex items-center gap-1 font-medium">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  Bytes Verified Immutable
                </span>
                <button
                  onClick={onOpenWorkspace}
                  className="px-3 py-1 rounded bg-slate-100 text-slate-700 hover:bg-indigo-50 hover:text-indigo-700 font-semibold text-[11px] transition-colors"
                >
                  View in Comparator
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
