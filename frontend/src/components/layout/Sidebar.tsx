import React, { useState } from 'react';
import {
  LayoutDashboard,
  Columns3,
  FileText,
  ShieldCheck,
  ChevronLeft,
  ChevronRight,
  Plus,
  Shield,
} from 'lucide-react';

interface SidebarProps {
  activeView: 'workspace' | 'dashboard' | 'documents' | 'audit';
  onChangeView: (view: 'workspace' | 'dashboard' | 'documents' | 'audit') => void;
  caseReference?: string;
  applicantName?: string;
  discrepancyCount: number;
  onNewCase: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeView,
  onChangeView,
  caseReference = "LOAN-2026-0891",
  applicantName = "Siddharth Jamdhade",
  discrepancyCount,
  onNewCase,
}) => {
  const [collapsed, setCollapsed] = useState(false);

  const navItems = [
    {
      id: 'workspace' as const,
      label: 'Investigation Workspace',
      icon: Columns3,
      badge: discrepancyCount > 0 ? `${discrepancyCount} flags` : undefined,
      badgeColor: 'bg-red-500/20 text-red-300 border border-red-500/30',
    },
    {
      id: 'dashboard' as const,
      label: 'Reconciliation Overview',
      icon: LayoutDashboard,
    },
    {
      id: 'documents' as const,
      label: 'Document Packets',
      icon: FileText,
      badge: '4 files',
      badgeColor: 'bg-slate-800 text-slate-300 border border-slate-700',
    },
    {
      id: 'audit' as const,
      label: 'Cryptographic Audit',
      icon: ShieldCheck,
      badge: 'SHA-256',
      badgeColor: 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30',
    },
  ];

  return (
    <aside
      className={`h-screen bg-slate-900 text-slate-300 flex flex-col justify-between transition-all duration-200 z-30 select-none flex-shrink-0 border-r border-slate-800 ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Top Branding */}
      <div>
        <div className="h-16 px-4 flex items-center justify-between border-b border-slate-800/80">
          {!collapsed ? (
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-sm shadow-indigo-600/40">
                <Shield className="w-4 h-4" />
              </div>
              <div>
                <span className="font-bold text-base text-white tracking-tight flex items-center gap-1.5">
                  ProofLens
                  <span className="text-[10px] px-1.5 py-0.2 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-mono font-normal">
                    v0.3
                  </span>
                </span>
                <p className="text-[10px] text-slate-400 -mt-0.5 font-medium">Evidence Workspace</p>
              </div>
            </div>
          ) : (
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white mx-auto shadow-sm shadow-indigo-600/40">
              <Shield className="w-4 h-4" />
            </div>
          )}

          <button
            onClick={() => setCollapsed(!collapsed)}
            className="hidden lg:flex w-6 h-6 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 items-center justify-center transition-colors"
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronLeft className="w-3.5 h-3.5" />}
          </button>
        </div>

        {/* Active Case Context Pill */}
        {!collapsed && (
          <div className="p-3 mx-3 mt-3 rounded-xl bg-slate-800/70 border border-slate-700/60">
            <div className="flex items-center justify-between text-[11px] text-slate-400 mb-1">
              <span className="uppercase font-semibold tracking-wider text-[10px] text-indigo-400">
                Active Packet
              </span>
              <span className="font-mono text-[10px] text-slate-300">{caseReference}</span>
            </div>
            <div className="text-xs font-semibold text-white truncate">{applicantName}</div>
            <div className="mt-2 pt-2 border-t border-slate-700/50 flex items-center justify-between text-[10px]">
              <span className="text-slate-400">Loan Dossier</span>
              <button
                onClick={onNewCase}
                className="text-indigo-400 hover:text-indigo-300 font-medium inline-flex items-center gap-1"
              >
                <Plus className="w-3 h-3" />
                <span>Switch / New</span>
              </button>
            </div>
          </div>
        )}

        {/* Navigation Section */}
        <nav className="p-3 space-y-1">
          <div className={`px-2 mb-2 text-[10px] font-semibold tracking-wider uppercase text-slate-500 ${collapsed ? 'hidden' : 'block'}`}>
            Investigations
          </div>

          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeView === item.id;

            return (
              <button
                key={item.id}
                onClick={() => onChangeView(item.id)}
                className={`w-full flex items-center rounded-lg transition-all text-xs font-medium ${
                  collapsed
                    ? 'justify-center py-2.5 px-0'
                    : 'justify-between px-3 py-2.5'
                } ${
                  isActive
                    ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-900/50 font-semibold'
                    : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'
                }`}
                title={collapsed ? item.label : undefined}
              >
                <div className="flex items-center space-x-3 min-w-0">
                  <Icon className={`w-4 h-4 flex-shrink-0 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                  {!collapsed && <span className="truncate">{item.label}</span>}
                </div>

                {!collapsed && item.badge && (
                  <span
                    className={`text-[10px] px-1.5 py-0.5 rounded-full font-mono font-medium ${item.badgeColor}`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Bottom Profile / Sovereign Indicator */}
      <div className="p-3 border-t border-slate-800">
        {!collapsed ? (
          <div className="space-y-2">
            <div className="flex items-center space-x-2.5 px-2 py-1.5 rounded-lg bg-slate-800/40">
              <div className="w-7 h-7 rounded-full bg-slate-700 flex items-center justify-center text-xs font-bold text-slate-200">
                SJ
              </div>
              <div className="min-w-0 flex-1">
                <div className="text-xs font-semibold text-white truncate">Siddharth J.</div>
                <div className="text-[10px] text-emerald-400 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                  Sovereign Reviewer
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between text-[11px] text-slate-500 px-2 pt-1">
              <span>Zero-Accusation Core</span>
              <span className="font-mono text-[10px]">WAL Offline</span>
            </div>
          </div>
        ) : (
          <div className="flex justify-center">
            <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-xs font-bold text-slate-200" title="Siddharth J. • Sovereign Reviewer">
              SJ
            </div>
          </div>
        )}
      </div>
    </aside>
  );
};
