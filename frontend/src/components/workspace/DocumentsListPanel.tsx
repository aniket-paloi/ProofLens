import React, { useRef, useState } from 'react';
import {
  FileText,
  AlertCircle,
  CheckCircle2,
  Clock,
  Layers,
  ChevronDown,
  Upload,
  Download,
} from 'lucide-react';
import { getDocumentDownloadUrl } from '../../services/api';

export interface PacketDocument {
  id: string;
  name: string;
  type: 'APPLICATION_FORM' | 'SALARY_SLIP' | 'BANK_STATEMENT';
  pages: number;
  size: string;
  status: 'PROCESSED' | 'PROCESSING' | 'PENDING';
  checksum: string;
}

export interface InvestigationClaimItem {
  id: string;
  title: string;
  category: 'INCOME' | 'TRANSACTION' | 'TEXT_LAYER' | 'IDENTITY';
  declaredValue: string;
  extractedValue: string;
  sourceDoc: string;
  targetDoc: string;
  pageNumber: number;
  status: 'DISCREPANCY' | 'MATCHED' | 'WARNING';
  discrepancyDelta?: string;
  summary: string;
  coordinates: { page: number; ymin: number; xmin: number; ymax: number; xmax: number };
}

interface DocumentsListPanelProps {
  documents: PacketDocument[];
  claims: InvestigationClaimItem[];
  selectedClaimId: string | null;
  onSelectClaim: (claim: InvestigationClaimItem) => void;
  selectedDocId: string | null;
  onSelectDoc: (docId: string) => void;
  onUploadDocFiles?: (files: File[]) => Promise<void>;
  onOpenDocumentsView?: () => void;
}

export const DocumentsListPanel: React.FC<DocumentsListPanelProps> = ({
  documents,
  claims,
  selectedClaimId,
  onSelectClaim,
  selectedDocId,
  onSelectDoc,
  onUploadDocFiles,
  onOpenDocumentsView,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [filterTab, setFilterTab] = useState<'ALL' | 'DISCREPANCIES' | 'MATCHED' | 'WARNINGS'>('ALL');
  const [docExpanded, setDocExpanded] = useState(true);
  const [uploading, setUploading] = useState(false);

  const filteredClaims = claims.filter((c) => {
    if (filterTab === 'DISCREPANCIES') return c.status === 'DISCREPANCY';
    if (filterTab === 'MATCHED') return c.status === 'MATCHED';
    if (filterTab === 'WARNINGS') return c.status === 'WARNING';
    return true;
  });

  const discrepancyCount = claims.filter((c) => c.status === 'DISCREPANCY').length;
  const matchedCount = claims.filter((c) => c.status === 'MATCHED').length;
  const warningCount = claims.filter((c) => c.status === 'WARNING').length;

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0 || !onUploadDocFiles) return;
    setUploading(true);
    try {
      await onUploadDocFiles(Array.from(files));
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleDownload = (e: React.MouseEvent, docId: string, filename: string) => {
    e.stopPropagation();
    const link = document.createElement('a');
    link.href = getDocumentDownloadUrl(docId);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="w-80 h-full bg-white border-r border-[#E8E8E6] flex flex-col flex-shrink-0 select-none">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        multiple
        accept=".pdf,.png,.jpg"
        className="hidden"
      />

      {/* Panel 1 Header */}
      <div className="p-4 border-b border-[#E8E8E6] flex items-center justify-between">
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider text-neutral-400">
            PANEL 1 • PACKET DOSSIER
          </span>
          <div className="text-sm font-bold text-[#18181B] mt-0.5">packet claims.</div>
        </div>
        <div className="flex items-center space-x-1">
          <button
            onClick={() => {
              if (onUploadDocFiles && fileInputRef.current) {
                fileInputRef.current.click();
              } else if (onOpenDocumentsView) {
                onOpenDocumentsView();
              }
            }}
            disabled={uploading}
            className="p-1.5 rounded-full border border-[#E8E8E6] bg-[#F4F4F2] text-neutral-700 hover:text-black hover:bg-neutral-200 transition-colors"
            title="Upload Supplemental Document"
          >
            <Upload className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Packet Documents Accordion Strip */}
      <div className="p-3 border-b border-[#E8E8E6] bg-[#FBFBF9]">
        <div
          onClick={() => setDocExpanded(!docExpanded)}
          className="flex items-center justify-between cursor-pointer text-xs font-semibold text-neutral-700 py-1"
        >
          <span className="flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-neutral-800" />
            <span>Submitted Files ({documents.length})</span>
          </span>
          <ChevronDown className={`w-3.5 h-3.5 text-neutral-400 transition-transform ${docExpanded ? 'rotate-180' : ''}`} />
        </div>

        {docExpanded && (
          <div className="mt-2 space-y-1.5">
            {documents.map((doc) => {
              const isSelected = selectedDocId === doc.id;
              return (
                <div
                  key={doc.id}
                  onClick={() => onSelectDoc(doc.id)}
                  className={`p-2.5 rounded-2xl border text-xs cursor-pointer transition-all flex items-center justify-between group ${
                    isSelected
                      ? 'bg-white border-[#121212] shadow-xs text-[#18181B]'
                      : 'bg-white border-[#E8E8E6] text-neutral-600 hover:border-neutral-300'
                  }`}
                >
                  <div className="flex items-center space-x-2 min-w-0">
                    <FileText className={`w-3.5 h-3.5 flex-shrink-0 ${isSelected ? 'text-[#121212]' : 'text-neutral-400'}`} />
                    <span className="truncate text-[11px] font-medium">{doc.name}</span>
                  </div>

                  <div className="flex items-center space-x-1.5 flex-shrink-0">
                    <button
                      onClick={(e) => handleDownload(e, doc.id, doc.name)}
                      className="p-1 rounded-full opacity-60 hover:opacity-100 hover:bg-[#F4F4F2] text-neutral-600"
                      title="Download Document"
                    >
                      <Download className="w-3 h-3" />
                    </button>
                    <span className="text-[10px] text-neutral-400 font-mono">
                      {doc.pages}p
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Claims Filter Tabs */}
      <div className="p-2 border-b border-[#E8E8E6] flex items-center space-x-1 text-[11px] font-medium bg-white">
        <button
          onClick={() => setFilterTab('ALL')}
          className={`flex-1 py-1.5 rounded-full text-center transition-colors ${
            filterTab === 'ALL'
              ? 'bg-[#121212] text-white font-semibold'
              : 'text-neutral-500 hover:text-black hover:bg-[#F4F4F2]'
          }`}
        >
          All ({claims.length})
        </button>
        <button
          onClick={() => setFilterTab('DISCREPANCIES')}
          className={`flex-1 py-1.5 rounded-full text-center transition-colors ${
            filterTab === 'DISCREPANCIES'
              ? 'bg-rose-100 text-rose-900 font-semibold'
              : 'text-neutral-500 hover:text-rose-700 hover:bg-rose-50'
          }`}
        >
          Gaps ({discrepancyCount})
        </button>
        <button
          onClick={() => setFilterTab('MATCHED')}
          className={`flex-1 py-1.5 rounded-full text-center transition-colors ${
            filterTab === 'MATCHED'
              ? 'bg-emerald-100 text-emerald-900 font-semibold'
              : 'text-neutral-500 hover:text-emerald-700 hover:bg-emerald-50'
          }`}
        >
          Verified ({matchedCount})
        </button>
        <button
          onClick={() => setFilterTab('WARNINGS')}
          className={`flex-1 py-1.5 rounded-full text-center transition-colors ${
            filterTab === 'WARNINGS'
              ? 'bg-amber-100 text-amber-900 font-semibold'
              : 'text-neutral-500 hover:text-amber-700 hover:bg-amber-50'
          }`}
        >
          Inquiry ({warningCount})
        </button>
      </div>

      {/* Extracted Claims Scroll Area */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2 bg-[#FBFBF9]">
        {filteredClaims.length === 0 ? (
          <div className="p-8 text-center text-xs text-neutral-400">
            No claims found for this filter.
          </div>
        ) : (
          filteredClaims.map((claim) => {
            const isSelected = selectedClaimId === claim.id;
            return (
              <div
                key={claim.id}
                onClick={() => onSelectClaim(claim)}
                className={`p-3 rounded-2xl border text-xs cursor-pointer transition-all ${
                  isSelected
                    ? 'bg-white border-[#121212] shadow-xs'
                    : 'bg-white border-[#E8E8E6] hover:border-neutral-300'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[10px] font-mono font-semibold uppercase px-2 py-0.5 rounded-full bg-[#F4F4F2] text-neutral-600">
                    {claim.category}
                  </span>

                  {claim.status === 'DISCREPANCY' && (
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-50 text-rose-800 border border-rose-200 flex items-center gap-1">
                      <AlertCircle className="w-2.5 h-2.5" />
                      GAP
                    </span>
                  )}
                  {claim.status === 'MATCHED' && (
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 flex items-center gap-1">
                      <CheckCircle2 className="w-2.5 h-2.5" />
                      VERIFIED
                    </span>
                  )}
                  {claim.status === 'WARNING' && (
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200 flex items-center gap-1">
                      <Clock className="w-2.5 h-2.5" />
                      INQUIRY
                    </span>
                  )}
                </div>

                <div className="font-semibold text-[#18181B] text-[11px] leading-snug mb-1">
                  {claim.title}
                </div>

                <div className="flex items-center justify-between text-[10px] text-neutral-500 font-mono mb-1.5">
                  <span>Declared: {claim.declaredValue}</span>
                  <span className={claim.status === 'DISCREPANCY' ? 'text-rose-700 font-bold' : ''}>
                    Observed: {claim.extractedValue}
                  </span>
                </div>

                {claim.discrepancyDelta && (
                  <div className="text-[10px] font-semibold text-rose-700 bg-rose-50/70 p-1.5 rounded-xl border border-rose-100 mb-1.5">
                    {claim.discrepancyDelta}
                  </div>
                )}

                <div className="text-[10px] text-neutral-400 truncate flex items-center justify-between">
                  <span>{claim.sourceDoc}</span>
                  <span>p.{claim.pageNumber}</span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
