"use client";

import { authAPI, getApiErrorMessage } from "@/lib/api";
import {
  Zap, Loader2, AlertCircle, ArrowRight,
  LockKeyhole, Sparkles, ShieldCheck,
} from "lucide-react";
import { startTransition, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) router.replace("/");
  }, [router]);

  const openDemoWorkspace = () => {
    localStorage.setItem("token", "demo-token-local");
    localStorage.setItem("demo", "true");
    localStorage.setItem(
      "user",
      JSON.stringify({ id: "demo", email: "demo@viralai.app", name: "Demo Creator" })
    );
    startTransition(() => router.push("/"));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      let res;
      if (isLogin) {
        res = await authAPI.login({ email, password });
      } else {
        res = await authAPI.register({ email, name, password });
      }
      localStorage.setItem("token", res.access_token);
      localStorage.setItem("user", JSON.stringify(res.user));
      startTransition(() => router.push("/"));
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "Something went wrong. Please try again."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen grid lg:grid-cols-[1.05fr_0.95fr] p-4 md:p-6 relative z-10 gap-6">

      {/* ── Left panel ────────────────────────────────────────── */}
      <div className="surface-panel hidden lg:flex flex-col justify-between p-10">
        <div>
          <div className="hero-kicker">Creator cockpit</div>
          <h1 className="text-4xl font-bold leading-tight max-w-lg">
            Plan smarter posts, score virality, and ship faster content.
          </h1>
          <p className="mt-4 max-w-xl text-base" style={{ color: "var(--text-muted)" }}>
            Blend trend discovery, content generation, and strategy planning into one flow.
            Each button runs exactly one AI agent — no black boxes.
          </p>
        </div>
        <div className="status-strip">
          <div className="glass-card p-5">
            <p className="text-xs uppercase tracking-[0.24em]" style={{ color: "var(--text-dim)" }}>Trend Scout</p>
            <p className="mt-2 text-xl font-semibold">Real-time hashtag + angle discovery</p>
          </div>
          <div className="glass-card p-5">
            <p className="text-xs uppercase tracking-[0.24em]" style={{ color: "var(--text-dim)" }}>Content Studio</p>
            <p className="mt-2 text-xl font-semibold">Hook → Caption → Hashtags → Score</p>
          </div>
          <div className="glass-card p-5">
            <p className="text-xs uppercase tracking-[0.24em]" style={{ color: "var(--text-dim)" }}>Strategy</p>
            <p className="mt-2 text-xl font-semibold">Seven-day calendar + growth forecast</p>
          </div>
        </div>
      </div>

      {/* ── Right panel ───────────────────────────────────────── */}
      <div className="w-full flex items-center justify-center">
        <div className="w-full max-w-md">

          {/* Logo */}
          <div className="flex items-center justify-center gap-3 mb-8 animate-fade-in">
            <div className="w-12 h-12 rounded-xl flex items-center justify-center"
              style={{ background: "linear-gradient(135deg, var(--accent), var(--accent-cyan))" }}>
              <Zap size={24} color="white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Viral AI</h1>
              <p className="text-xs" style={{ color: "var(--text-dim)" }}>Content Intelligence Platform</p>
            </div>
          </div>

          {/* Card */}
          <div className="glass-card p-8 animate-fade-in-up">

            {/* Toggle */}
            <div className="auth-toggle">
              <button type="button"
                className={`auth-toggle-button ${isLogin ? "auth-toggle-button-active" : ""}`}
                onClick={() => { setIsLogin(true); setError(""); }}>
                Sign In
              </button>
              <button type="button"
                className={`auth-toggle-button ${!isLogin ? "auth-toggle-button-active" : ""}`}
                onClick={() => { setIsLogin(false); setError(""); }}>
                Create Account
              </button>
            </div>

            <h2 className="text-xl font-bold mb-1 text-center">
              {isLogin ? "Welcome Back" : "Create Account"}
            </h2>
            <p className="text-sm text-center mb-6" style={{ color: "var(--text-muted)" }}>
              {isLogin ? "Sign in to your account" : "Start your content journey"}
            </p>

            {error && (
              <div className="flex items-center gap-2 p-3 rounded-xl mb-4"
                style={{ background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)" }}>
                <AlertCircle size={16} style={{ color: "#ef4444" }} />
                <p className="text-xs" style={{ color: "#ef4444" }}>{error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              {!isLogin && (
                <div>
                  <label className="text-sm font-medium mb-1.5 block" style={{ color: "var(--text-muted)" }}>
                    Full Name *
                  </label>
                  <input
                    className="input-field"
                    placeholder="John Doe"
                    value={name}
                    onChange={e => setName(e.target.value)}
                    required
                  />
                </div>
              )}

              <div>
                <label className="text-sm font-medium mb-1.5 block" style={{ color: "var(--text-muted)" }}>
                  Email *
                </label>
                <input
                  className="input-field"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-1.5 block" style={{ color: "var(--text-muted)" }}>
                  Password *
                </label>
                <input
                  className="input-field"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                />
              </div>

              <button type="submit" className="btn-primary w-full justify-center" disabled={loading}>
                {loading
                  ? <><Loader2 size={16} className="animate-spin" /> Processing...</>
                  : <><LockKeyhole size={16} /> {isLogin ? "Sign In" : "Create Account"} <ArrowRight size={16} /></>}
              </button>
            </form>

            <button
              type="button"
              className="btn-secondary w-full justify-center mt-3"
              onClick={openDemoWorkspace}
            >
              <Sparkles size={16} /> Continue in Demo Mode
            </button>

            <div className="mt-5 grid gap-2">
              <div className="auth-meta-row"><ShieldCheck size={14} /> Local demo works even if the API is offline.</div>
              <div className="auth-meta-row"><Zap size={14} /> All pages have demo fallbacks — nothing breaks.</div>
            </div>

            <div className="mt-6 text-center">
              <button
                onClick={() => { setIsLogin(!isLogin); setError(""); }}
                className="text-sm hover:underline"
                style={{ color: "var(--accent-light)" }}
              >
                {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
              </button>
            </div>

            <div className="mt-4 p-3 rounded-xl text-center"
              style={{ background: "rgba(124,58,237,0.08)", border: "1px solid rgba(124,58,237,0.15)" }}>
              <p className="text-[11px]" style={{ color: "var(--text-dim)" }}>
                💡 Demo mode skips the backend entirely — full UI works immediately.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}