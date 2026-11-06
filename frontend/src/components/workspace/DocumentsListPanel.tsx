import React, { useState } from 'react';
import {
  FileText,
  AlertCircle,
  CheckCircle2,
  Clock,
  Layers,
  ChevronDown,
  Upload,
} from 'lucide-react';

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
  onUploadDoc: () => void;
}

export const DocumentsListPanel: React.FC<DocumentsListPanelProps> = ({
  documents,
  claims,
  selectedClaimId,
  onSelectClaim,
  selectedDocId,
  onSelectDoc,
  onUploadDoc,
}) => {
  const [filterTab, setFilterTab] = useState<'ALL' | 'DISCREPANCIES' | 'MATCHED' | 'WARNINGS'>('ALL');
  const [docExpanded, setDocExpanded] = useState(true);

  const filteredClaims = claims.filter((c) => {
    if (filterTab === 'DISCREPANCIES') return c.status === 'DISCREPANCY';
    if (filterTab === 'MATCHED') return c.status === 'MATCHED';
    if (filterTab === 'WARNINGS') return c.status === 'WARNING';
    return true;
  });

  const discrepancyCount = claims.filter((c) => c.status === 'DISCREPANCY').length;
  const matchedCount = claims.filter((c) => c.status === 'MATCHED').length;
  const warningCount = claims.filter((c) => c.status === 'WARNING').length;

  return (
    <div className="w-80 h-full bg-white border-r border-slate-200 flex flex-col flex-shrink-0 select-none">
      {/* Panel 1 Header */}
      <div className="p-4 border-b border-slate-200 flex items-center justify-between">
        <div>
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Panel 1 • Documents & Claims
          </h2>
          <div className="text-sm font-bold text-slate-900 mt-0.5">Packet Dossier</div>
        </div>
        <button
          onClick={onUploadDoc}
          className="p-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 hover:text-slate-900 transition-colors"
          title="Upload New Document"
        >
          <Upload className="w-4 h-4" />
        </button>
      </div>

      {/* Packet Documents Accordion Strip */}
      <div className="p-3 border-b border-slate-200 bg-slate-50/60">
        <div
          onClick={() => setDocExpanded(!docExpanded)}
          className="flex items-center justify-between cursor-pointer text-xs font-semibold text-slate-700 py-1"
        >
          <span className="flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-indigo-600" />
            <span>Submitted Files ({documents.length})</span>
          </span>
          <ChevronDown className={`w-3.5 h-3.5 text-slate-400 transition-transform ${docExpanded ? 'rotate-180' : ''}`} />
        </div>

        {docExpanded && (
          <div className="mt-2 space-y-1.5">
            {documents.map((doc) => {
              const isSelected = selectedDocId === doc.id;
              return (
                <div
                  key={doc.id}
                  onClick={() => onSelectDoc(doc.id)}
                  className={`p-2 rounded-lg border text-xs cursor-pointer transition-all flex items-center justify-between ${
                    isSelected
                      ? 'bg-indigo-50/80 border-indigo-200 text-indigo-950 font-medium'
                      : 'bg-white border-slate-200 text-slate-700 hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-center space-x-2 min-w-0">
                    <FileText className={`w-3.5 h-3.5 flex-shrink-0 ${isSelected ? 'text-indigo-600' : 'text-slate-400'}`} />
                    <span className="truncate text-[11px] font-medium">{doc.name}</span>
                  </div>
                  <span className="text-[10px] text-slate-400 font-mono flex-shrink-0">
                    {doc.pages}p
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Claims Filter Tabs */}
      <div className="p-2 border-b border-slate-200 flex items-center space-x-1 text-[11px] font-medium bg-white">
        <button
          onClick={() => setFilterTab('ALL')}
          className={`flex-1 py-1.5 rounded-md text-center transition-colors ${
            filterTab === 'ALL'
              ? 'bg-slate-900 text-white font-semibold'
              : 'text-slate-500 hover:text-slate-800 hover:bg-slate-100'
          }`}
        >
          All ({claims.length})
        </button>
        <button
          onClick={() => setFilterTab('DISCREPANCIES')}
          className={`flex-1 py-1.5 rounded-md text-center transition-colors ${
            filterTab === 'DISCREPANCIES'
              ? 'bg-red-600 text-white font-semibold'
              : 'text-red-600 hover:bg-red-50'
          }`}
        >
          Flags ({discrepancyCount})
        </button>
        <button
          onClick={() => setFilterTab('MATCHED')}
          className={`flex-1 py-1.5 rounded-md text-center transition-colors ${
            filterTab === 'MATCHED'
              ? 'bg-emerald-600 text-white font-semibold'
              : 'text-emerald-700 hover:bg-emerald-50'
          }`}
        >
          Match ({matchedCount})
        </button>
        <button
          onClick={() => setFilterTab('WARNINGS')}
          className={`flex-1 py-1.5 rounded-md text-center transition-colors ${
            filterTab === 'WARNINGS'
              ? 'bg-amber-600 text-white font-semibold'
              : 'text-amber-700 hover:bg-amber-50'
          }`}
        >
          Warn ({warningCount})
        </button>
      </div>

      {/* Claims List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {filteredClaims.map((claim) => {
          const isSelected = selectedClaimId === claim.id;

          const isDiscrepancy = claim.status === 'DISCREPANCY';
          const isMatched = claim.status === 'MATCHED';
          const isWarning = claim.status === 'WARNING';

          return (
            <div
              key={claim.id}
              onClick={() => onSelectClaim(claim)}
              className={`p-3 rounded-xl border text-xs cursor-pointer transition-all ${
                isSelected
                  ? 'bg-indigo-50/70 border-indigo-400 ring-1 ring-indigo-400 shadow-sm'
                  : 'bg-white border-slate-200 hover:border-slate-300 shadow-subtle'
              }`}
            >
              {/* Status & Category Bar */}
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-[10px] font-bold tracking-wider uppercase text-slate-400 font-mono">
                  {claim.category}
                </span>

                {isDiscrepancy && (
                  <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-red-100 text-red-700 border border-red-200">
                    <AlertCircle className="w-2.5 h-2.5" />
                    DISCREPANCY
                  </span>
                )}
                {isMatched && (
                  <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
                    <CheckCircle2 className="w-2.5 h-2.5" />
                    RECONCILED
                  </span>
                )}
                {isWarning && (
                  <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-200">
                    <Clock className="w-2.5 h-2.5" />
                    NEEDS CHECK
                  </span>
                )}
              </div>

              {/* Title */}
              <div className="font-semibold text-slate-900 text-xs mb-1">
                {claim.title}
              </div>

              {/* Values Comparison Row */}
              <div className="mt-2 pt-2 border-t border-slate-100 grid grid-cols-2 gap-2 text-[11px]">
                <div className="p-1.5 rounded-lg bg-slate-50 border border-slate-100">
                  <div className="text-[9px] uppercase tracking-wider font-semibold text-slate-400">
                    Declared
                  </div>
                  <div className="font-mono font-bold text-slate-800 truncate">
                    {claim.declaredValue}
                  </div>
                </div>

                <div className="p-1.5 rounded-lg bg-slate-50 border border-slate-100">
                  <div className="text-[9px] uppercase tracking-wider font-semibold text-slate-400">
                    Extracted
                  </div>
                  <div className={`font-mono font-bold truncate ${isDiscrepancy ? 'text-red-600' : 'text-slate-800'}`}>
                    {claim.extractedValue}
                  </div>
                </div>
              </div>

              {/* Source Document Tag */}
              <div className="mt-2 flex items-center justify-between text-[10px] text-slate-400">
                <span className="truncate">{claim.sourceDoc}</span>
                <span className="font-mono">p.{claim.pageNumber}</span>
              </div>
            </div>
          );
        })}

        {filteredClaims.length === 0 && (
          <div className="p-6 text-center text-xs text-slate-400">
            No claims found matching the current filter.
          </div>
        )}
      </div>
    </div>
  );
};
