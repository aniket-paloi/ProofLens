import React, { useState } from 'react';
import {
  DocumentsListPanel,
  PacketDocument,
  InvestigationClaimItem,
} from './DocumentsListPanel';
import { EvidenceViewerPanel } from './EvidenceViewerPanel';
import { FindingsInspectorPanel } from './FindingsInspectorPanel';

interface InvestigationWorkspaceProps {
  documents: PacketDocument[];
  claims: InvestigationClaimItem[];
  onSubmitReview: (claimId: string, disposition: string, reason: string) => Promise<void>;
  onUploadDoc: () => void;
}

export const InvestigationWorkspace: React.FC<InvestigationWorkspaceProps> = ({
  documents,
  claims,
  onSubmitReview,
  onUploadDoc,
}) => {
  const [selectedDocId, setSelectedDocId] = useState<string | null>(documents[0]?.id || null);
  const [selectedClaim, setSelectedClaim] = useState<InvestigationClaimItem | null>(claims[0] || null);

  const handleSelectClaim = (claim: InvestigationClaimItem) => {
    setSelectedClaim(claim);
  };

  return (
    <div className="flex-1 h-[calc(100vh-4rem)] flex overflow-hidden bg-slate-100">
      {/* PANEL 1: Documents & Extracted Packet Claims (Left) */}
      <DocumentsListPanel
        documents={documents}
        claims={claims}
        selectedClaimId={selectedClaim?.id || null}
        onSelectClaim={handleSelectClaim}
        selectedDocId={selectedDocId}
        onSelectDoc={setSelectedDocId}
        onUploadDoc={onUploadDoc}
      />

      {/* PANEL 2: Evidence Viewer & Side-by-Side Comparator (Center) */}
      <EvidenceViewerPanel
        activeClaim={selectedClaim}
        onSelectClaim={(id) => {
          const found = claims.find((c) => c.id === id);
          if (found) setSelectedClaim(found);
        }}
      />

      {/* PANEL 3: Findings & Quick View Inspector (Right) */}
      <FindingsInspectorPanel
        activeClaim={selectedClaim}
        onSubmitReview={onSubmitReview}
      />
    </div>
  );
};

