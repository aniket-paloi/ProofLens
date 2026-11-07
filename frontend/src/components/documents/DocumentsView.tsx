import React, { useRef, useState } from 'react';
import {
  FileText,
  Upload,
  CheckCircle2,
  Hash,
  ShieldCheck,
  Download,
  Eye,
  X,
  FileCheck,
} from 'lucide-react';
import { PacketDocument } from '../workspace/DocumentsListPanel';
import { getDocumentDownloadUrl, getPageImageUrl } from '../../services/api';

interface DocumentsViewProps {
  documents: PacketDocument[];
  onUploadDoc: (files: File[]) => Promise<void>;
  onOpenWorkspace: (docId?: string) => void;
  caseReference: string;
}

export const DocumentsView: React.FC<DocumentsViewProps> = ({
  documents,
  onUploadDoc,
  onOpenWorkspace,
  caseReference,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [selectedPreviewDoc, setSelectedPreviewDoc] = useState<PacketDocument | null>(null);
  const [previewPage, setPreviewPage] = useState<number>(1);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    setUploading(true);
    setErrorMsg(null);
    try {
      await onUploadDoc(Array.from(files));
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to upload document');
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleTriggerUpload = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleDownload = (docId: string, filename: string) => {
    const link = document.createElement('a');
    link.href = getDocumentDownloadUrl(docId);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="flex-1 h-[calc(100vh-4rem)] overflow-y-auto p-8 bg-[#FBFBF9] select-none text-[#18181B]">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Hidden file input */}
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          multiple
          accept=".pdf,.png,.jpg,.jpeg"
          className="hidden"
        />

        {/* Header Section */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#E8E8E6]">
          <div>
            <div className="flex items-center space-x-2 text-[11px] font-bold tracking-wider text-neutral-400 uppercase mb-1">
              <span className="w-2 h-2 rounded-full bg-emerald-600" />
              <span>Immutable Evidence Storage • Case {caseReference}</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-[#18181B]">
              submitted document packets.
            </h1>
            <p className="text-xs text-neutral-500 mt-1">
              Every document is stored immutably with SHA-256 integrity verification. Download, inspect, or add supplemental packet files.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={handleTriggerUpload}
              disabled={uploading}
              className="inline-flex items-center space-x-1.5 px-5 py-2.5 text-xs font-semibold rounded-full bg-[#121212] text-white hover:bg-neutral-800 transition-colors shadow-sm disabled:opacity-50"
            >
              <Upload className="w-3.5 h-3.5" />
              <span>{uploading ? 'Ingesting PDF...' : 'Add Supplemental File'}</span>
            </button>
          </div>
        </div>

        {errorMsg && (
          <div className="p-3 bg-rose-50 border border-rose-200 rounded-2xl text-rose-800 text-xs flex items-center justify-between">
            <span>{errorMsg}</span>
            <button onClick={() => setErrorMsg(null)} className="font-bold underline ml-2">Dismiss</button>
          </div>
        )}

        {/* Upload Drop Zone Banner */}
        <div
          onClick={handleTriggerUpload}
          className="p-8 rounded-3xl border-2 border-dashed border-[#E8E8E6] bg-white hover:bg-[#F4F4F2] cursor-pointer transition-colors text-center flex flex-col items-center justify-center space-y-2"
        >
          <div className="w-10 h-10 rounded-full bg-[#F4F4F2] border border-[#E8E8E6] flex items-center justify-center text-neutral-600">
            <Upload className="w-5 h-5" />
          </div>
          <div>
            <span className="text-xs font-semibold text-[#18181B]">
              Click to select financial documents or drop PDFs here
            </span>
            <p className="text-[11px] text-neutral-400 mt-0.5">
              Supports PDF Loan Application, Salary Slips, and Bank Statements up to 50MB
            </p>
          </div>
        </div>

        {/* Documents Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="p-6 rounded-3xl bg-white border border-[#E8E8E6] shadow-xs flex flex-col justify-between hover:border-neutral-300 transition-all"
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-9 h-9 rounded-2xl bg-[#F4F4F2] border border-[#E8E8E6] flex items-center justify-center text-neutral-800">
                      <FileText className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-[#18181B]">{doc.name}</div>
                      <span className="text-[10px] uppercase font-mono font-semibold text-neutral-400">
                        {doc.type}
                      </span>
                    </div>
                  </div>

                  <span className="text-[10px] px-2.5 py-1 rounded-full font-bold bg-emerald-50 text-emerald-800 border border-emerald-200 flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" />
                    {doc.status}
                  </span>
                </div>

                <div className="p-3 rounded-2xl bg-[#FBFBF9] border border-[#E8E8E6] text-[11px] font-mono text-neutral-600 space-y-1.5 mb-5">
                  <div className="flex items-center justify-between text-neutral-500">
                    <span>Pages: {doc.pages}</span>
                    <span>Size: {doc.size}</span>
                  </div>
                  <div className="text-[10px] text-neutral-400 break-all flex items-center gap-1 pt-1 border-t border-[#E8E8E6]">
                    <Hash className="w-3 h-3 flex-shrink-0" />
                    <span>{doc.checksum}</span>
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-[#E8E8E6] flex items-center justify-between">
                <span className="text-[11px] text-emerald-800 flex items-center gap-1 font-medium">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  Bytes Verified Immutable
                </span>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleDownload(doc.id, doc.name)}
                    className="p-2 rounded-full bg-[#F4F4F2] border border-[#E8E8E6] text-neutral-700 hover:text-black hover:bg-neutral-200 transition-colors"
                    title="Download Original PDF Document"
                  >
                    <Download className="w-3.5 h-3.5" />
                  </button>

                  <button
                    onClick={() => {
                      setSelectedPreviewDoc(doc);
                      setPreviewPage(1);
                    }}
                    className="p-2 rounded-full bg-[#F4F4F2] border border-[#E8E8E6] text-neutral-700 hover:text-black hover:bg-neutral-200 transition-colors"
                    title="Quick Preview Pages"
                  >
                    <Eye className="w-3.5 h-3.5" />
                  </button>

                  <button
                    onClick={() => onOpenWorkspace(doc.id)}
                    className="px-3.5 py-1.5 rounded-full bg-[#121212] text-white font-semibold text-[11px] hover:bg-neutral-800 transition-colors"
                  >
                    View in Workspace
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* QUICK DOCUMENT PREVIEW MODAL */}
      {selectedPreviewDoc && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white border border-[#E8E8E6] rounded-3xl p-6 max-w-2xl w-full shadow-2xl flex flex-col max-h-[90vh]">
            <div className="flex items-center justify-between pb-3 border-b border-[#E8E8E6]">
              <div className="flex items-center space-x-2">
                <FileCheck className="w-4 h-4 text-neutral-700" />
                <span className="text-xs font-bold text-[#18181B] truncate max-w-sm">
                  {selectedPreviewDoc.name}
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#F4F4F2] text-neutral-500 font-mono">
                  Page {previewPage} of {selectedPreviewDoc.pages}
                </span>
              </div>

              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleDownload(selectedPreviewDoc.id, selectedPreviewDoc.name)}
                  className="px-3 py-1 rounded-full text-xs font-semibold bg-[#F4F4F2] border border-[#E8E8E6] text-neutral-700 hover:text-black flex items-center gap-1"
                >
                  <Download className="w-3 h-3" />
                  <span>Download</span>
                </button>
                <button
                  onClick={() => setSelectedPreviewDoc(null)}
                  className="w-7 h-7 rounded-full bg-[#F4F4F2] flex items-center justify-center text-neutral-500 hover:text-black"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            {/* Document Render Canvas */}
            <div className="flex-1 overflow-auto p-4 flex items-center justify-center bg-[#FBFBF9] my-3 rounded-2xl border border-[#E8E8E6]">
              <img
                src={getPageImageUrl(selectedPreviewDoc.id, previewPage)}
                alt={`Page ${previewPage} of ${selectedPreviewDoc.name}`}
                className="max-h-[60vh] object-contain shadow-sm rounded-lg border border-[#E8E8E6]"
                onError={(e) => {
                  // Fallback visual canvas if derivative png is not on disk yet
                  (e.target as HTMLElement).style.display = 'none';
                  const parent = (e.target as HTMLElement).parentElement;
                  if (parent && !parent.querySelector('.preview-fallback')) {
                    const fallback = document.createElement('div');
                    fallback.className = 'preview-fallback p-8 text-center text-xs text-neutral-500';
                    fallback.innerHTML = `
                      <div class="font-bold text-neutral-800 text-sm mb-1">${selectedPreviewDoc.name}</div>
                      <div class="text-[11px] text-neutral-400 mb-4">Original PDF preserved in storage/originals</div>
                      <div class="text-[10px] font-mono bg-white p-3 rounded-xl border border-neutral-200">
                        SHA-256: ${selectedPreviewDoc.checksum}
                      </div>
                    `;
                    parent.appendChild(fallback);
                  }
                }}
              />
            </div>

            {/* Modal Footer with Page Navigation */}
            <div className="flex items-center justify-between pt-2 border-t border-[#E8E8E6]">
              <div className="flex items-center space-x-1">
                <button
                  disabled={previewPage <= 1}
                  onClick={() => setPreviewPage((p) => Math.max(1, p - 1))}
                  className="px-3 py-1 rounded-full text-xs font-semibold bg-[#F4F4F2] border border-[#E8E8E6] text-neutral-700 disabled:opacity-30"
                >
                  Previous
                </button>
                <button
                  disabled={previewPage >= selectedPreviewDoc.pages}
                  onClick={() => setPreviewPage((p) => Math.min(selectedPreviewDoc.pages, p + 1))}
                  className="px-3 py-1 rounded-full text-xs font-semibold bg-[#F4F4F2] border border-[#E8E8E6] text-neutral-700 disabled:opacity-30"
                >
                  Next
                </button>
              </div>

              <button
                onClick={() => {
                  const docId = selectedPreviewDoc.id;
                  setSelectedPreviewDoc(null);
                  onOpenWorkspace(docId);
                }}
                className="px-4 py-1.5 rounded-full text-xs font-semibold bg-[#121212] text-white hover:bg-neutral-800"
              >
                Inspect in 3-Panel Comparator →
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
