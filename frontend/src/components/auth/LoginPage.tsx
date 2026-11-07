import React, { useState } from 'react';
import { ArrowLeft, Lock, ShieldCheck, User } from 'lucide-react';

interface LoginPageProps {
  onLoginSuccess: (reviewerName: string) => void;
  onBackToLanding: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess, onBackToLanding }) => {
  const [email, setEmail] = useState('siddharth.reviewer@prooflens.local');
  const [password, setPassword] = useState('••••••••••••');
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      onLoginSuccess('Siddharth B. Jamdhade');
    }, 400);
  };

  const handleGuestLogin = () => {
    onLoginSuccess('Guest Reviewer');
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
          <span>Local Session</span>
        </div>
      </div>

      {/* Main Card */}
      <div className="w-full max-w-md mx-auto my-auto">
        <div className="bg-white border border-[#E8E8E6] rounded-3xl p-8 sm:p-10 shadow-sm">
          {/* Logo & Headline */}
          <div className="mb-6">
            <div className="w-10 h-10 rounded-full bg-[#121212] flex items-center justify-center text-white font-bold text-sm mb-4">
              P
            </div>
            <div className="text-[11px] font-bold tracking-widest uppercase text-neutral-400">
              SECURE REVIEWER AUTHENTICATION
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-[#18181B] mt-1">
              welcome back.
            </h2>
            <p className="text-xs text-neutral-600 mt-1 leading-relaxed">
              Sign in to examine financial claims, review visual forensic evidence, and record audit commitments.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-neutral-700 mb-1.5">
                Reviewer Identity / Email
              </label>
              <div className="relative">
                <input
                  type="text"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full text-xs px-4 py-3 rounded-2xl bg-[#F4F4F2] border border-[#E8E8E6] text-[#18181B] focus:outline-none focus:ring-1 focus:ring-[#121212]"
                />
                <User className="w-4 h-4 text-neutral-400 absolute right-3.5 top-3.5" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-neutral-700 mb-1.5">
                Password
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

          <div className="mt-5 pt-4 border-t border-[#E8E8E6] text-center">
            <button
              onClick={handleGuestLogin}
              className="text-xs font-semibold text-neutral-600 hover:text-black transition-colors"
            >
              Continue as Guest Reviewer (Demo Mode) →
            </button>
          </div>
        </div>

        <div className="text-center mt-6 text-[11px] text-neutral-400">
          ProofLens Sovereign Reviewer System • Cryptographic Local Session
        </div>
      </div>

      <div />
    </div>
  );
};

