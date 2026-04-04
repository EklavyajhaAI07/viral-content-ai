"use client";

import Sidebar from "@/components/Sidebar";
import { getApiErrorMessage, trendsAPI } from "@/lib/api";
import type { TrendResponse, HashtagItem, ViralAngle } from "@/types";
import {
  TrendingUp, Search, Flame, Clock, Hash,
  Loader2, AlertCircle, Zap,
} from "lucide-react";
import { useState } from "react";

const platforms = ["all", "instagram", "tiktok", "youtube", "twitter", "linkedin"];

// ── Demo fallback (matches TrendResponse shape) ───────────────────────────────
function buildDemoTrends(topic: string, platform: string): TrendResponse {
  const slug = topic.toLowerCase().replace(/\s+/g, "");
  return {
    job_id: "demo",
    topic,
    platform,
    hashtags: [
      { tag: `#${slug}`, velocity: 91, strongest_on: "instagram", peak_in_hours: 6 },
      { tag: `#${slug}Tips`, velocity: 84, strongest_on: "tiktok", peak_in_hours: 10 },
      { tag: `#${slug}2025`, velocity: 78, strongest_on: "youtube", peak_in_hours: 14 },
      { tag: `#viral${slug.charAt(0).toUpperCase() + slug.slice(1)}`, velocity: 72, strongest_on: "instagram", peak_in_hours: 8 },
      { tag: `#${slug}Hacks`, velocity: 65, strongest_on: "tiktok", peak_in_hours: 12 },
    ],
    viral_angles: [
      { angle: `The ${topic} truth nobody tells you`, description: "Contrarian take with curiosity gap — very high share rate.", virality_score: 88 },
      { angle: `I tried ${topic} for 30 days`, description: "Personal experiment format — builds trust and comment engagement.", virality_score: 82 },
      { angle: `${topic} is changing everything — here's why`, description: "Trend authority angle — strong for YouTube and LinkedIn.", virality_score: 75 },
    ],
    niche_classification: "lifestyle",
    overall_trend_velocity: 80,
    has_real_data: false,
    status: "completed",
    cached: false,
    elapsed_seconds: 0,
  };
}

export default function TrendsPage() {
  const [topic, setTopic] = useState("");
  const [platform, setPlatform] = useState("all");
  const [data, setData] = useState<TrendResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [searched, setSearched] = useState(false);
  const [isDemo, setIsDemo] = useState(false);

  const handleDiscover = async () => {
    if (!topic.trim()) return;
    setLoading(true); setError(""); setData(null); setIsDemo(false);

    try {
      // New API: GET /api/trends?topic=&platform= returns flat TrendResponse
      const res = await trendsAPI.discover({ topic: topic.trim(), platform });
      setData(res);
      setSearched(true);
    } catch (err: unknown) {
      setData(buildDemoTrends(topic.trim(), platform));
      setIsDemo(true);
      setSearched(true);
      setError(`Backend unavailable — showing demo data. ${getApiErrorMessage(err, "")}`.trim());
    } finally {
      setLoading(false);
    }
  };

  const velocityColor = (v: number) =>
    v >= 80 ? "#10b981" : v >= 60 ? "#f59e0b" : "#ef4444";

  return (
    <div className="app-shell">
      <Sidebar />
      <main className="page-content">

        {/* ── Hero ────────────────────────────────────────────── */}
        <div className="page-hero animate-fade-in">
          <div className="hero-kicker">Trend intelligence</div>
          <h1 className="text-2xl md:text-4xl font-bold flex items-center gap-3">
            <TrendingUp size={30} style={{ color: "var(--accent-light)" }} />
            Trend Discovery
          </h1>
          <p className="mt-3 max-w-2xl" style={{ color: "var(--text-muted)" }}>
            Search any niche to surface rising hashtags, velocity scores, and the top viral angles right now.
          </p>
          <div className="status-strip mt-5">
            <div className="status-chip">Real-time Google Trends + YouTube data</div>
            <div className="status-chip">Velocity scores per hashtag</div>
            <div className="status-chip">Top 3 viral content angles</div>
          </div>
        </div>

        {/* ── Search Form ─────────────────────────────────────── */}
        <div className="glass-card p-6 mb-6 animate-fade-in-up">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <label className="text-sm font-medium mb-2 block" style={{ color: "var(--text-muted)" }}>
                Topic or Niche
              </label>
              <div className="relative">
                <input
                  type="text"
                  className="input-field pl-11"
                  placeholder="e.g., AI productivity tools, fitness, cooking..."
                  value={topic}
                  onChange={e => setTopic(e.target.value)}
                  onKeyDown={e => e.key === "Enter" && handleDiscover()}
                />
              </div>
            </div>
            <div className="w-full md:w-48">
              <label className="text-sm font-medium mb-2 block" style={{ color: "var(--text-muted)" }}>Platform</label>
              <select className="input-field" value={platform} onChange={e => setPlatform(e.target.value)}>
                {platforms.map(p => (
                  <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
                ))}
              </select>
            </div>
            <div className="flex items-end">
              <button className="btn-primary w-full md:w-auto" onClick={handleDiscover} disabled={loading || !topic.trim()}>
                {loading
                  ? <><Loader2 size={16} className="animate-spin" /> Discovering...</>
                  : <><Flame size={16} /> Discover Trends</>}
              </button>
            </div>
          </div>
        </div>

        {/* ── Error ───────────────────────────────────────────── */}
        {error && (
          <div className="flex items-center gap-3 p-4 rounded-xl mb-6"
            style={{ background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)" }}>
            <AlertCircle size={18} style={{ color: "#ef4444" }} />
            <p className="text-sm" style={{ color: "#ef4444" }}>{error}</p>
          </div>
        )}

        {searched && (
          <div className="source-banner mb-6">
            <span className="badge badge-platform">{isDemo ? "Offline demo" : "live api"}</span>
            <p>{isDemo ? "Demo trend data shown — connect backend for live results." : `Real trend data for "${topic}"`}</p>
          </div>
        )}

        {/* ── Skeleton ────────────────────────────────────────── */}
        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="glass-card p-5">
                <div className="skeleton h-5 w-3/4 mb-3" />
                <div className="skeleton h-4 w-full mb-2" />
                <div className="skeleton h-4 w-2/3 mb-4" />
                <div className="flex gap-2">
                  {[1, 2, 3].map(j => <div key={j} className="skeleton h-6 w-16 rounded-full" />)}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* ── Results ─────────────────────────────────────────── */}
        {!loading && data && (
          <div className="space-y-6 animate-fade-in-up">

            {/* Overall velocity */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="glass-card p-4 text-center">
                <p className="text-2xl font-bold" style={{ color: velocityColor(data.overall_trend_velocity) }}>
                  {data.overall_trend_velocity}
                </p>
                <p className="text-xs mt-1" style={{ color: "var(--text-dim)" }}>Overall Velocity</p>
              </div>
              <div className="glass-card p-4 text-center">
                <p className="text-2xl font-bold" style={{ color: "var(--accent-light)" }}>{data.hashtags.length}</p>
                <p className="text-xs mt-1" style={{ color: "var(--text-dim)" }}>Trending Hashtags</p>
              </div>
              <div className="glass-card p-4 text-center">
                <p className="text-2xl font-bold" style={{ color: "var(--accent-cyan)" }}>{data.viral_angles.length}</p>
                <p className="text-xs mt-1" style={{ color: "var(--text-dim)" }}>Viral Angles</p>
              </div>
              <div className="glass-card p-4 text-center">
                <p className="text-lg font-bold capitalize" style={{ color: "var(--warning)" }}>{data.niche_classification}</p>
                <p className="text-xs mt-1" style={{ color: "var(--text-dim)" }}>Niche</p>
              </div>
            </div>

            {/* Hashtags */}
            <div className="glass-card p-6">
              <h2 className="text-lg font-semibold flex items-center gap-2 mb-4">
                <Hash size={20} style={{ color: "var(--accent-light)" }} /> Trending Hashtags
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {data.hashtags.map((h: HashtagItem, i: number) => (
                  <div key={i} className="p-4 rounded-xl" style={{ background: "var(--bg-secondary)" }}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-sm" style={{ color: "var(--accent-light)" }}>{h.tag}</span>
                      <span className="text-xs font-bold px-2 py-1 rounded-full"
                        style={{ background: `${velocityColor(h.velocity)}20`, color: velocityColor(h.velocity) }}>
                        {h.velocity} velocity
                      </span>
                    </div>
                    <div className="h-1.5 rounded-full mb-2" style={{ background: "var(--border)" }}>
                      <div className="h-full rounded-full transition-all duration-700"
                        style={{ width: `${h.velocity}%`, background: velocityColor(h.velocity) }} />
                    </div>
                    <div className="flex items-center justify-between text-xs" style={{ color: "var(--text-dim)" }}>
                      <span>Strongest on <span style={{ color: "var(--text-muted)" }}>{h.strongest_on}</span></span>
                      <span className="flex items-center gap-1"><Clock size={10} /> Peak in {h.peak_in_hours}h</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Viral Angles */}
            <div className="glass-card p-6">
              <h2 className="text-lg font-semibold flex items-center gap-2 mb-4">
                <Zap size={20} style={{ color: "var(--warning)" }} /> Top Viral Angles
              </h2>
              <div className="space-y-3">
                {data.viral_angles.map((a: ViralAngle, i: number) => (
                  <div key={i} className="p-4 rounded-xl flex items-start gap-4"
                    style={{ background: "var(--bg-secondary)", border: "1px solid var(--border)" }}>
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                      style={{ background: `${velocityColor(a.virality_score)}20` }}>
                      <span className="text-sm font-bold" style={{ color: velocityColor(a.virality_score) }}>
                        #{i + 1}
                      </span>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <h3 className="font-semibold text-sm">{a.angle}</h3>
                        <span className="text-xs font-bold" style={{ color: velocityColor(a.virality_score) }}>
                          {a.virality_score}/100
                        </span>
                      </div>
                      <p className="text-xs" style={{ color: "var(--text-muted)" }}>{a.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        )}

        {/* ── Empty State ──────────────────────────────────────── */}
        {!loading && !searched && (
          <div className="text-center py-16 animate-fade-in">
            <div className="w-20 h-20 rounded-2xl mx-auto mb-5 flex items-center justify-center animate-pulse-glow"
              style={{ background: "linear-gradient(135deg, rgba(124,58,237,0.15), rgba(6,182,212,0.1))", border: "1px solid rgba(124,58,237,0.2)" }}>
              <TrendingUp size={36} style={{ color: "var(--accent-light)" }} />
            </div>
            <h3 className="text-xl font-semibold mb-2">Discover What&apos;s Trending</h3>
            <p className="text-sm max-w-md mx-auto" style={{ color: "var(--text-muted)" }}>
              Enter a topic and the Trend Scout agent will analyse real-time Google Trends and YouTube data to surface hashtags, velocity scores, and the best viral angles.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}