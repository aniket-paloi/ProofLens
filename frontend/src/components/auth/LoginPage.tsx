import React, { useState } from 'react';
import { ArrowLeft, Lock, ShieldCheck, User, Mail, Briefcase, CheckCircle2 } from 'lucide-react';

export interface StoredUser {
  name: string;
  email: string;
  role: string;
  organization: string;
  registeredAt: string;
}

interface LoginPageProps {
  onLoginSuccess: (user: StoredUser) => void;
  onBackToLanding: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess, onBackToLanding }) => {
  const [mode, setMode] = useState<'signin' | 'signup'>('signin');
  const [email, setEmail] = useState('aniket.paloi@prooflens.local');
  const [password, setPassword] = useState('••••••••••••');
  const [fullName, setFullName] = useState('Aniket Paloi');
  const [role, setRole] = useState('Principal Sovereign Reviewer');
  const [organization, setOrganization] = useState('Sovereign Underwriting Systems');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleSignIn = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      // Check if user already exists in localStorage
      const existingRaw = localStorage.getItem('prooflens_registered_users');
      let registeredUsers: StoredUser[] = [];
      try {
        if (existingRaw) registeredUsers = JSON.parse(existingRaw);
      } catch {
        registeredUsers = [];
      }

      const match = registeredUsers.find((u) => u.email.toLowerCase() === email.toLowerCase());
      const activeUser: StoredUser = match || {
        name: fullName || 'Aniket Paloi',
        email,
        role: role || 'Lead Underwriting Officer',
        organization: organization || 'Sovereign Underwriting Labs',
        registeredAt: new Date().toISOString(),
      };

      localStorage.setItem('prooflens_active_user', JSON.stringify(activeUser));
      setLoading(false);
      onLoginSuccess(activeUser);
    }, 350);
  };

  const handleSignUp = (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName || !email) {
      setMessage('Please provide your name and work email.');
      return;
    }
    setLoading(true);
    setTimeout(() => {
      const newUser: StoredUser = {
        name: fullName,
        email,
        role: role || 'Underwriting Specialist',
        organization: organization || 'Independent Reviewer',
        registeredAt: new Date().toISOString(),
      };

      // Persist to user registry
      const existingRaw = localStorage.getItem('prooflens_registered_users');
      let registeredUsers: StoredUser[] = [];
      try {
        if (existingRaw) registeredUsers = JSON.parse(existingRaw);
      } catch {
        registeredUsers = [];
      }

      registeredUsers.push(newUser);
      localStorage.setItem('prooflens_registered_users', JSON.stringify(registeredUsers));
      localStorage.setItem('prooflens_active_user', JSON.stringify(newUser));

      setLoading(false);
      onLoginSuccess(newUser);
    }, 400);
  };

  const handleGuestLogin = () => {
    const guestUser: StoredUser = {
      name: 'Aniket Paloi (Sovereign Lead)',
      email: 'aniket.paloi@prooflens.local',
      role: 'Sovereign Investigation Lead',
      organization: 'Underwriting Forensics Guild',
      registeredAt: new Date().toISOString(),
    };
    localStorage.setItem('prooflens_active_user', JSON.stringify(guestUser));
    onLoginSuccess(guestUser);
  };

  return (
    <div className="min-h-screen bg-[#FBFBF9] text-[#18181B] flex flex-col justify-between p-6 font-sans">
      {/* Top Bar */}
      <div className="w-full max-w-md mx-auto pt-4 flex items-center justify-between">
        <button
          onClick={onBackToLanding}
          className="inline-flex items-center space-x-1.5 text-xs font-semibold text-neutral-600 hover:text-black transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Home</span>
        </button>

        <div className="flex items-center space-x-1.5 text-xs text-neutral-500">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
          <span>Cryptographic Local Session</span>
        </div>
      </div>

      {/* Main Card */}
      <div className="w-full max-w-md mx-auto my-auto py-6">
        <div className="bg-white border border-[#E8E8E6] rounded-3xl p-8 sm:p-10 shadow-sm">
          {/* Logo & Headline */}
          <div className="mb-6">
            <div className="w-10 h-10 rounded-full bg-[#121212] flex items-center justify-center text-white font-bold text-sm mb-4">
              P
            </div>
            <div className="text-[11px] font-bold tracking-widest uppercase text-neutral-400">
              SOVEREIGN REVIEWER SYSTEM
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-[#18181B] mt-1">
              {mode === 'signin' ? 'welcome back.' : 'create reviewer identity.'}
            </h2>
            <p className="text-xs text-neutral-600 mt-1 leading-relaxed">
              {mode === 'signin'
                ? 'Sign in to examine financial claims, verify evidence hashes, and record immutable audit events.'
                : 'Register your reviewer credentials. Your session and audit dispositions will be tied to this profile.'}
            </p>
          </div>

          {/* Mode Switcher Tabs */}
          <div className="flex items-center p-1 bg-[#F4F4F2] rounded-full border border-[#E8E8E6] mb-6">
            <button
              type="button"
              onClick={() => setMode('signin')}
              className={`flex-1 py-1.5 text-xs font-semibold rounded-full transition-all ${
                mode === 'signin'
                  ? 'bg-white text-[#121212] shadow-xs'
                  : 'text-neutral-500 hover:text-neutral-900'
              }`}
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => setMode('signup')}
              className={`flex-1 py-1.5 text-xs font-semibold rounded-full transition-all ${
                mode === 'signup'
                  ? 'bg-white text-[#121212] shadow-xs'
                  : 'text-neutral-500 hover:text-neutral-900'
              }`}
            >
              Register New Reviewer
            </button>
          </div>

          {message && (
            <div className="mb-4 p-3 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs">
              {message}
            </div>
          )}

          {mode === 'signin' ? (
            <form onSubmit={handleSignIn} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-neutral-700 mb-1.5">
                  Reviewer Work Email
                </label>
                <div className="relative">
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full text-xs px-4 py-3 rounded-2xl bg-[#F4F4F2] border border-[#E8E8E6] text-[#18181B] focus:outline-none focus:ring-1 focus:ring-[#121212]"
                    placeholder="reviewer@institution.com"
                  />
                  <Mail className="w-4 h-4 text-neutral-400 absolute right-3.5 top-3.5" />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-neutral-700 mb-1.5">
                  Security Passphrase
                </label>
                <div className="relative">
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full text-xs px-4 py-3 rounded-2xl bg-[#F4F4F2] border border-[#E8E8E6] text-[#18181B] focus:outline-none focus:ring-1 focus:ring-[#121212]"
                  />
                  <Lock className="w-4 h-4 text-neutral-400 absolute right-3.5 top-3.5" />
                </div>
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3 rounded-full bg-[#121212] text-white text-xs font-semibold hover:bg-neutral-800 transition-colors shadow-sm disabled:opacity-50"
                >
                  {loading ? 'Authenticating...' : 'Sign In as Sovereign Reviewer'}
                </button>
              </div>
            </form>
          ) : (
            <form onSubmit={handleSignUp} className="space-y-3.5">
              <div>
                <label className="block text-xs font-semibold text-neutral-700 mb-1">
                  Full Name
                </label>
                <div className="relative">
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="e.g. Aniket Paloi"
                    className="w-full text-xs px-4 py-2.5 rounded-2xl bg-[#F4F4F2] border border-[#E8E8E6] text-[#18181B] focus:outline-none focus:ring-1 focus:ring-[#121212]"
                  />
                  <User className="w-4 h-4 text-neutral-400 absolute right-3.5 top-3" />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-neutral-700 mb-1">
                  Work Email Address
                </label>
                <div className="relative">
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="e.g. aniket.paloi@underwriting.com"
                    className="w-full text-xs px-4 py-2.5 rounded-2xl bg-[#F4F4F2] border border-[#E8E8E6] text-[#18181B] focus:outline-none focus:ring-1 focus:ring-[#121212]"
                  />
                  <Mail className="w-4 h-4 text-neutral-400 absolute right-3.5 top-3" />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-neutral-700 mb-1">
                  Role / Specialization
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    placeholder="e.g. Lead Credit Underwriter"
                    className="w-full text-xs px-4 py-2.5 rounded-2xl bg-[#F4F4F2] border border-[#E8E8E6] text-[#18181B] focus:outline-none focus:ring-1 focus:ring-[#121212]"
                  />
                  <Briefcase className="w-4 h-4 text-neutral-400 absolute right-3.5 top-3" />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-neutral-700 mb-1">
                  Organization / Entity
                </label>
                <input
                  type="text"
                  value={organization}
                  onChange={(e) => setOrganization(e.target.value)}
                  placeholder="e.g. Apex Underwriting Labs"
                  className="w-full text-xs px-4 py-2.5 rounded-2xl bg-[#F4F4F2] border border-[#E8E8E6] text-[#18181B] focus:outline-none focus:ring-1 focus:ring-[#121212]"
                />
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3 rounded-full bg-[#121212] text-white text-xs font-semibold hover:bg-neutral-800 transition-colors shadow-sm disabled:opacity-50"
                >
                  {loading ? 'Creating Profile...' : 'Complete Registration & Enter Workspace'}
                </button>
              </div>
            </form>
          )}

          <div className="mt-5 pt-4 border-t border-[#E8E8E6] text-center">
            <button
              onClick={handleGuestLogin}
              className="text-xs font-semibold text-neutral-600 hover:text-black transition-colors"
            >
              Instant Sovereign Demo Access (Aniket Paloi) →
            </button>
          </div>
        </div>

        <div className="text-center mt-6 text-[11px] text-neutral-400 flex items-center justify-center space-x-2">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
          <span>Reviewer identity is stored locally in browser storage</span>
        </div>
      </div>

      <div />
    </div>
  );
};
