import React from 'react';
import { FileText, FolderKanban, Plus, AlertCircle, ShieldCheck } from 'lucide-react';

interface BottomBarProps {
  activeTab: 'overview' | 'documents' | 'findings' | 'audit';
  onChangeTab: (tab: 'overview' | 'documents' | 'findings' | 'audit') => void;
  onCenterAction: () => void;
  findingCount: number;
}

export const BottomBar: React.FC<BottomBarProps> = ({
  activeTab,
  onChangeTab,
  onCenterAction,
  findingCount,
}) => {
  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-stoic-card/90 backdrop-blur-md border-t border-stoic-border py-2 px-6">
      <div className="max-w-md mx-auto flex items-center justify-between relative">
        {/* Overview Tab */}
        <button
          onClick={() => onChangeTab('overview')}
          className={`flex flex-col items-center space-y-1 text-[11px] font-medium transition-colors ${
            activeTab === 'overview' ? 'text-stoic-dark font-bold' : 'text-stoic-muted hover:text-stoic-text'
          }`}
        >
          <FileText className="w-5 h-5" />
          <span>Overview</span>
        </button>

        {/* Documents Tab */}
        <button
          onClick={() => onChangeTab('documents')}
          className={`flex flex-col items-center space-y-1 text-[11px] font-medium transition-colors ${
            activeTab === 'documents' ? 'text-stoic-dark font-bold' : 'text-stoic-muted hover:text-stoic-text'
          }`}
        >
          <FolderKanban className="w-5 h-5" />
          <span>Documents</span>
        </button>

        {/* Center Floating Action Button (Stoic circular black + button) */}
        <div className="-mt-6">
          <button
            onClick={onCenterAction}
            className="w-14 h-14 rounded-full bg-stoic-dark text-white flex items-center justify-center shadow-lg hover:scale-105 active:scale-95 transition-all"
            title="Start Investigation Run"
          >
            <Plus className="w-6 h-6 stroke-[2.5]" />
          </button>
        </div>

        {/* Findings Tab */}
        <button
          onClick={() => onChangeTab('findings')}
          className={`flex flex-col items-center space-y-1 text-[11px] font-medium transition-colors relative ${
            activeTab === 'findings' ? 'text-stoic-dark font-bold' : 'text-stoic-muted hover:text-stoic-text'
          }`}
        >
          <AlertCircle className="w-5 h-5" />
          <span>Findings</span>
          {findingCount > 0 && (
            <span className="absolute -top-1 right-1 w-2 h-2 rounded-full bg-stoic-terracotta" />
          )}
        </button>

        {/* Audit Tab */}
        <button
          onClick={() => onChangeTab('audit')}
          className={`flex flex-col items-center space-y-1 text-[11px] font-medium transition-colors ${
            activeTab === 'audit' ? 'text-stoic-dark font-bold' : 'text-stoic-muted hover:text-stoic-text'
          }`}
        >
          <ShieldCheck className="w-5 h-5" />
          <span>Integrity</span>
        </button>
      </div>
    </div>
  );
};

