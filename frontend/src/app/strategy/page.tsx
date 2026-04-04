"use client";

import Sidebar from "@/components/Sidebar";
import { getApiErrorMessage, strategyAPI } from "@/lib/api";
import type { StrategyResponse } from "@/types";
import {
  Target, Loader2, AlertCircle, Rocket,
} from "lucide-react";
import { useState } from "react";

const platforms = ["instagram", "tiktok", "youtube", "linkedin", "twitter"];

// ── Demo fallback ─────────────────────────────────────────────────────────────
function demoStrategy(topic: string, platform: string): StrategyResponse {
  return {
    job_id: "demo", topic, platform,
    strategy: `## 7-Day Content Calendar for "${topic}"

**Day 1 — ${platform.charAt(0).toUpperCase() + platform.slice(1)}** | Reel | 7 PM
Topic: The biggest misconception about ${topic}
Hook: "Everyone's doing ${topic} wrong — here's the fix"

**Day 2 — TikTok** | Short | 6 PM
Topic: ${topic} in 60 seconds — the fast version
Hook: "No fluff. Here's ${topic} explained fast."

**Day 3 — YouTube** | Long-form | 3 PM
Topic: Complete ${topic} guide for beginners
Hook: "I spent 30 days on ${topic} so you don't have to"

**Day 4 — LinkedIn** | Post | 8 AM
Topic: What ${topic} taught me about building in public
Hook: "3 hard lessons from ${topic} that changed how I work"

**Day 5 — Instagram** | Carousel | 12 PM
Topic: ${topic} — 5 tools I actually use
Hook: "Swipe to see my exact ${topic} stack"

**Day 6 — Twitter/X** | Thread | 9 AM
Topic: ${topic} myths vs reality
Hook: "Hot take: most ${topic} advice is wrong. Thread 🧵"

**Day 7 — All platforms** | Repurpose best performer
Topic: Double down on Day 1-6 top post

---

## Cross-Platform Repurposing Plan
- **Instagram Reel** → trim to TikTok (add trending audio)
- **YouTube Long-form** → clip 3 shorts from top moments
- **LinkedIn Post** → expand into Twitter thread
- **Twitter Thread** → combine into LinkedIn article

---

## 30-Day Growth Forecast
- Follower growth: +200–400 new followers
- Total reach: 80,000–150,000 impressions
- Best performing format: Short-form video

---

## Top 3 Content Gaps
1. Behind-the-scenes of ${topic} process (nobody shows this)
2. ${topic} failures and what went wrong (high empathy share rate)
3. Comparing ${topic} tools head-to-head (high search intent)

---

## A/B Tests to Run
- **Test 1**: Hook with question vs bold statement → measure comment rate
- **Test 2**: Post at 7 PM vs 9 PM → measure reach in first 2 hours`,
    status: "demo", cached: false, elapsed_seconds: 0,
  };
}

export default function StrategyPage() {
  const [topic, setTopic] = useState("");
  const [platform, setPlatform] = useState("instagram");
  const [viralityScore, setViralityScore] = useState<number>(75);
  const [result, setResult] = useState<StrategyResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isDemo, setIsDemo] = useState(false);

  const handleGenerate = async () => {
    if (!topic.trim()) return;
    setLoading(true); setError(""); setResult(null); setIsDemo(false);
    try {
      // New API: returns flat StrategyResponse — no .data wrapper
      const res = await strategyAPI.generate({ topic: topic.trim(), platform, virality_score: viralityScore });
      setResult(res);
    } catch (e: unknown) {
      setResult(demoStrategy(topic.trim(), platform));
      setIsDemo(true);
      setError(`Backend unavailable — showing demo strategy. ${getApiErrorMessage(e, "")}`.trim());
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <Sidebar />
      <main className="page-content">

        {/* ── Hero ────────────────────────────────────────────── */}
        <div className="page-hero animate-fade-in">
          <div className="hero-kicker">Planning engine</div>
          <h1 className="text-2xl md:text-4xl font-bold flex items-center gap-3">
            <Target size={28} style={{ color: "var(--accent-light)" }} /> Strategy Generator
          </h1>
          <p className="mt-3 max-w-2xl" style={{ color: "var(--text-muted)" }}>
            Turn one topic into a 7-day calendar, repurposing flow, content gap analysis, and 30-day growth forecast.
          </p>
          <div className="status-strip mt-5">
            <div className="status-chip">7-day publishing map</div>
            <div className="status-chip">Cross-platform repurposing plan</div>
            <div className="status-chip">Forecast + A/B test suggestions</div>
          </div>
        </div>

        {/* ── Form ────────────────────────────────────────────── */}
        <div className="glass-card p-6 mb-6 animate-fade-in-up">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-1">
              <label className="text-sm font-medium mb-2 block" style={{ color: "var(--text-muted)" }}>Topic *</label>
              <input className="input-field" placeholder="e.g., Personal branding for developers"
                value={topic} onChange={e => setTopic(e.target.value)}
                onKeyDown={e => e.key === "Enter" && handleGenerate()} />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block" style={{ color: "var(--text-muted)" }}>Primary Platform</label>
              <select className="input-field" value={platform} onChange={e => setPlatform(e.target.value)}>
                {platforms.map(p => <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>)}
              </select>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block" style={{ color: "var(--text-muted)" }}>
                Virality Score <span className="text-xs font-normal">(from Content Studio)</span>
              </label>
              <input type="number" min={0} max={100} className="input-field"
                value={viralityScore} onChange={e => setViralityScore(Number(e.target.value))} />
            </div>
          </div>
          <div className="mt-4 flex justify-end">
            <button className="btn-primary" onClick={handleGenerate} disabled={loading || !topic.trim()}>
              {loading
                ? <><Loader2 size={16} className="animate-spin" /> Generating...</>
                : <><Rocket size={16} /> Generate Strategy</>}
            </button>
          </div>
          <p className="text-xs mt-3" style={{ color: "var(--text-dim)" }}>
            💡 Tip: Run <strong>Predict Virality</strong> in Content Studio first, then paste the score here for a calibrated strategy.
          </p>
        </div>

        {/* ── Error ───────────────────────────────────────────── */}
        {error && (
          <div className="flex items-center gap-3 p-4 rounded-xl mb-6"
            style={{ background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)" }}>
            <AlertCircle size={18} style={{ color: "#ef4444" }} />
            <p className="text-sm" style={{ color: "#ef4444" }}>{error}</p>
          </div>
        )}

        {result && (
          <div className="source-banner mb-6">
            <span className="badge badge-platform">{isDemo ? "Offline demo" : "live api"}</span>
            <p>{isDemo ? "Demo strategy shown — connect backend for live AI output." : `Strategy generated for "${topic}" on ${platform}`}</p>
          </div>
        )}

        {/* ── Loading Skeleton ─────────────────────────────────── */}
        {loading && (
          <div className="space-y-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="glass-card p-6">
                <div className="skeleton h-6 w-48 mb-4" />
                <div className="skeleton h-4 w-full mb-2" />
                <div className="skeleton h-4 w-3/4" />
              </div>
            ))}
          </div>
        )}

        {/* ── Result ──────────────────────────────────────────── */}
        {!loading && result && (
          <div className="glass-card p-6 animate-fade-in-up">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Target size={20} style={{ color: "var(--accent-light)" }} />
              Strategy for &ldquo;{result.topic}&rdquo; — {result.platform}
            </h2>
            {/* Render strategy markdown as preformatted text */}
            <div className="prose prose-invert max-w-none">
              <pre className="whitespace-pre-wrap text-sm leading-relaxed"
                style={{ color: "var(--text-muted)", fontFamily: "inherit" }}>
                {result.strategy}
              </pre>
            </div>
            {result.elapsed_seconds > 0 && (
              <p className="text-xs mt-4" style={{ color: "var(--text-dim)" }}>
                Generated in {result.elapsed_seconds}s {result.cached ? "· Cached" : ""}
              </p>
            )}
          </div>
        )}

        {/* ── Empty State ──────────────────────────────────────── */}
        {!loading && !result && !error && (
          <div className="text-center py-16 animate-fade-in">
            <div className="w-20 h-20 rounded-2xl mx-auto mb-5 flex items-center justify-center animate-pulse-glow"
              style={{ background: "linear-gradient(135deg, rgba(16,185,129,0.15), rgba(124,58,237,0.1))", border: "1px solid rgba(16,185,129,0.2)" }}>
              <Target size={36} style={{ color: "var(--success)" }} />
            </div>
            <h3 className="text-xl font-semibold mb-2">AI Strategy Generator</h3>
            <p className="text-sm max-w-lg mx-auto" style={{ color: "var(--text-muted)" }}>
              Enter a topic and get a complete 7-day content calendar, cross-platform repurposing plan, content gaps, A/B tests, and a 30-day growth forecast — all in one click.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}