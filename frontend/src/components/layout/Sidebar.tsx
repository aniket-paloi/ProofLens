import React, { useState } from 'react';
import {
  Columns3,
  Scale,
  Search,
  Share2,
  CheckSquare,
  FileDown,
  FolderKanban,
  ShieldCheck,
  FlaskConical,
  BarChart3,
  ChevronLeft,
  ChevronRight,
  LogOut,
  Home,
} from 'lucide-react';

export type AppView =
  | 'landing'
  | 'login'
  | 'workspace'
  | 'reconciliation'
  | 'forensics'
  | 'graph'
  | 'coverage'
  | 'dossier'
  | 'documents'
  | 'audit'
  | 'lab'
  | 'analytics';

interface SidebarProps {
  activeView: AppView;
  onChangeView: (view: AppView) => void;
  caseReference?: string;
  applicantName?: string;
  discrepancyCount: number;
  onNewCase: () => void;
  onLogout: () => void;
  onGoToLanding: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeView,
  onChangeView,
  caseReference = "LOAN-2026-0891",
  applicantName = "Siddharth Jamdhade",
  discrepancyCount,
  onNewCase,
  onLogout,
  onGoToLanding,
}) => {
  const [collapsed, setCollapsed] = useState(false);

  const mainNavItems = [
    {
      id: 'workspace' as const,
      label: '3-Panel Workspace',
      icon: Columns3,
      badge: discrepancyCount > 0 ? `${discrepancyCount} flags` : undefined,
      badgeColor: 'bg-amber-900/40 text-amber-300 border border-amber-700/50',
    },
    {
      id: 'reconciliation' as const,
      label: 'Financial Reconciliation',
      icon: Scale,
    },
    {
      id: 'forensics' as const,
      label: 'Visual & Layer Forensics',
      icon: Search,
    },
    {
      id: 'graph' as const,
      label: 'Claim & Evidence Graph',
      icon: Share2,
    },
    {
      id: 'coverage' as const,
      label: 'Coverage Matrix',
      icon: CheckSquare,
    },
    {
      id: 'dossier' as const,
      label: 'Dossier Exporter',
      icon: FileDown,
    },
    {
      id: 'documents' as const,
      label: 'Document Packets',
      icon: FolderKanban,
      badge: '4 files',
      badgeColor: 'bg-neutral-800 text-neutral-300 border border-neutral-700',
    },
    {
      id: 'audit' as const,
      label: 'Cryptographic Audit',
      icon: ShieldCheck,
      badge: 'SHA-256',
      badgeColor: 'bg-emerald-950/60 text-emerald-300 border border-emerald-800/60',
    },
    {
      id: 'lab' as const,
      label: 'FraudSim & What-If Lab',
      icon: FlaskConical,
      badge: 'Bonus',
      badgeColor: 'bg-neutral-800 text-neutral-400 border border-neutral-700',
    },
    {
      id: 'analytics' as const,
      label: 'Reviewer Feedback',
      icon: BarChart3,
    },
  ];

  return (
    <aside
      className={`h-screen bg-[#121212] text-neutral-300 flex flex-col justify-between transition-all duration-200 z-30 select-none flex-shrink-0 border-r border-neutral-800 ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Top Branding */}
      <div>
        <div className="h-16 px-4 flex items-center justify-between border-b border-neutral-800">
          {!collapsed ? (
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-full bg-white text-[#121212] flex items-center justify-center font-black text-sm">
                P
              </div>
              <div>
                <span className="font-bold text-base text-white tracking-tight flex items-center gap-1.5">
                  prooflens.
                  <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-neutral-800 text-neutral-300 border border-neutral-700 font-mono font-normal">
                    v0.3
                  </span>
                </span>
                <p className="text-[10px] text-neutral-400 -mt-0.5 font-medium">Sovereign Evidence</p>
              </div>
            </div>
          ) : (
            <div className="w-8 h-8 rounded-full bg-white text-[#121212] flex items-center justify-center font-black text-sm mx-auto">
              P
            </div>
          )}

          <button
            onClick={() => setCollapsed(!collapsed)}
            className="hidden lg:flex w-6 h-6 rounded-md text-neutral-400 hover:text-white hover:bg-neutral-800 items-center justify-center transition-colors"
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronLeft className="w-3.5 h-3.5" />}
          </button>
        </div>

        {/* Active Case Context Pill */}
        {!collapsed && (
          <div className="p-3 mx-3 mt-3 rounded-2xl bg-neutral-900 border border-neutral-800">
            <div className="flex items-center justify-between mb-1">
              <span className="text-[10px] uppercase font-bold tracking-wider text-neutral-400">
                ACTIVE DOSSIER
              </span>
              <button
                onClick={onNewCase}
                className="text-[10px] font-semibold text-white hover:underline"
              >
                + Switch
              </button>
            </div>
            <div className="font-mono text-xs font-bold text-white truncate">
              {caseReference}
            </div>
            <div className="text-[11px] text-neutral-400 truncate mt-0.5">
              {applicantName}
            </div>
          </div>
        )}

        {/* Navigation Items */}
        <nav className="p-2 space-y-1 mt-2 overflow-y-auto max-h-[calc(100vh-280px)] scrollbar-none">
          {mainNavItems.map((item) => {
            const isActive = activeView === item.id;
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => onChangeView(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-white text-[#121212] font-semibold shadow-sm'
                    : 'text-neutral-400 hover:text-white hover:bg-neutral-800/60'
                }`}
                title={collapsed ? item.label : undefined}
              >
                <div className="flex items-center space-x-2.5 truncate">
                  <Icon className={`w-4 h-4 flex-shrink-0 ${isActive ? 'text-[#121212]' : 'text-neutral-400'}`} />
                  {!collapsed && <span className="truncate">{item.label}</span>}
                </div>
                {!collapsed && item.badge && (
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${item.badgeColor}`}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Bottom Footer Actions */}
      <div className="p-3 border-t border-neutral-800 space-y-1">
        <button
          onClick={onGoToLanding}
          className="w-full flex items-center space-x-2 px-3 py-2 rounded-xl text-xs font-medium text-neutral-400 hover:text-white hover:bg-neutral-800/60 transition-colors"
          title="Return to Public Landing Page"
        >
          <Home className="w-4 h-4 flex-shrink-0" />
          {!collapsed && <span>Public Portal</span>}
        </button>

        <button
          onClick={onLogout}
          className="w-full flex items-center space-x-2 px-3 py-2 rounded-xl text-xs font-medium text-neutral-400 hover:text-rose-400 hover:bg-neutral-800/60 transition-colors"
          title="Sign Out"
        >
          <LogOut className="w-4 h-4 flex-shrink-0" />
          {!collapsed && <span>Sign Out</span>}
        </button>
      </div>
    </aside>
  );
};
