"use client";

import Sidebar from "@/components/Sidebar";
import { generateDemoTrends } from "@/lib/demoData";
import { getApiErrorMessage, trendsAPI } from "@/lib/api";
import { TrendItem } from "@/types";
import {
  TrendingUp,
  Search,
  Flame,
  Clock,
  Hash,
  Loader2,
  AlertCircle,
  ArrowUp,
  ArrowDown,
} from "lucide-react";
import { useState } from "react";

const platforms = ["all", "instagram", "tiktok", "youtube", "twitter", "linkedin"];

export default function TrendsPage() {
  const [topic, setTopic] = useState("");
  const [platform, setPlatform] = useState("all");
  const [trends, setTrends] = useState<TrendItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [searched, setSearched] = useState(false);
  const [source, setSource] = useState("idle");

  const handleDiscover = async () => {
    if (!topic.trim()) return;
    setLoading(true);
    setError("");
    setTrends([]);
    try {
      const res = await trendsAPI.discover({ topic: topic.trim(), platform });
      const data = res.data?.trends || [];
      setTrends(data);
      setSource(res.source || "api");
      setSearched(true);
    } catch (err: unknown) {
      setTrends(generateDemoTrends(topic.trim(), platform));
      setSource("offline_demo");
      setSearched(true);
      setError(`Backend unavailable, so demo results are shown instead. ${getApiErrorMessage(err, "")}`.trim());
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const cls = status === "emerging" ? "badge-emerging" : status === "peak" ? "badge-peak" : "badge-declining";
    const Icon = status === "declining" ? ArrowDown : ArrowUp;
    return (
      <span className={`badge ${cls} flex items-center gap-1`}>
        <Icon size={10} />
        {status}
      </span>
    );
  };

  const getVelocityColor = (score: number) => {
    if (score >= 80) return "#10b981";
    if (score >= 60) return "#f59e0b";
    return "#ef4444";
  };

  return (
    <div className="app-shell">
      <Sidebar />
      <main className="page-content">
        {/* Header */}
        <div className="page-hero animate-fade-in">
          <div className="hero-kicker">Trend intelligence</div>
          <h1 className="text-2xl md:text-4xl font-bold flex items-center gap-3">
            <TrendingUp size={30} style={{ color: "var(--accent-light)" }} />
            Trend Discovery
          </h1>
          <p className="mt-3 max-w-2xl" style={{ color: "var(--text-muted)" }}>
            Search any niche to surface rising angles, velocity scores, hashtags, and platform fit.
          </p>
          <div className="status-strip mt-5">
            <div className="status-chip">8 seeded trend variations per query</div>
            <div className="status-chip">Velocity and peak timing included</div>
            <div className="status-chip">Demo fallback enabled for offline use</div>
          </div>
        </div>

        {/* Search Form */}
        <div className="glass-card p-6 mb-6 animate-fade-in-up">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <label className="text-sm font-medium mb-2 block" style={{ color: "var(--text-muted)" }}>
                Topic or Niche
              </label>
              <div className="relative">
                <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2" style={{ color: "var(--text-dim)" }} />
                <input
                  type="text"
                  className="input-field pl-11"
                  placeholder="e.g., AI productivity tools, fitness trends, cooking..."
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleDiscover()}
                />
              </div>
            </div>
            <div className="w-full md:w-48">
              <label className="text-sm font-medium mb-2 block" style={{ color: "var(--text-muted)" }}>
                Platform
              </label>
              <select
                className="input-field"
                value={platform}
                onChange={(e) => setPlatform(e.target.value)}
              >
                {platforms.map((p) => (
                  <option key={p} value={p}>
                    {p.charAt(0).toUpperCase() + p.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-end">
              <button
                className="btn-primary w-full md:w-auto"
                onClick={handleDiscover}
                disabled={loading || !topic.trim()}
              >
                {loading ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    Discovering...
                  </>
                ) : (
                  <>
                    <Flame size={16} />
                    Discover Trends
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div
            className="flex items-center gap-3 p-4 rounded-xl mb-6"
            style={{ background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)" }}
          >
            <AlertCircle size={18} style={{ color: "#ef4444" }} />
            <p className="text-sm" style={{ color: "#ef4444" }}>{error}</p>
          </div>
        )}

        {searched && source !== "idle" && (
          <div className="source-banner mb-6">
            <span className="badge badge-platform">
              {source === "offline_demo" ? "Offline demo" : source}
            </span>
            <p>
              {source === "offline_demo"
                ? "Search is still usable with seeded local trend data."
                : "Results were returned by the backend trend flow."}
            </p>
          </div>
        )}

        {/* Loading Skeleton */}
        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="glass-card p-5">
                <div className="skeleton h-5 w-3/4 mb-3" />
                <div className="skeleton h-4 w-full mb-2" />
                <div className="skeleton h-4 w-2/3 mb-4" />
                <div className="flex gap-2">
                  <div className="skeleton h-6 w-16 rounded-full" />
                  <div className="skeleton h-6 w-16 rounded-full" />
                  <div className="skeleton h-6 w-16 rounded-full" />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Results */}
        {!loading && trends.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">
                Found <span className="gradient-text">{trends.length} trends</span> for &quot;{topic}&quot;
              </h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 stagger-children">
              {trends.map((trend, i) => (
                <div key={i} className="glass-card p-5 group">
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="font-semibold text-sm pr-4 leading-snug">{trend.topic}</h3>
                    {getStatusBadge(trend.status)}
                  </div>

                  {/* Velocity Bar */}
                  <div className="mb-3">
                    <div className="flex justify-between text-xs mb-1">
                      <span style={{ color: "var(--text-dim)" }}>Velocity Score</span>
                      <span className="font-bold" style={{ color: getVelocityColor(trend.velocity_score) }}>
                        {trend.velocity_score}
                      </span>
                    </div>
                    <div className="h-1.5 rounded-full" style={{ background: "var(--bg-secondary)" }}>
                      <div
                        className="h-full rounded-full transition-all duration-1000"
                        style={{
                          width: `${trend.velocity_score}%`,
                          background: `linear-gradient(90deg, ${getVelocityColor(trend.velocity_score)}, ${getVelocityColor(trend.velocity_score)}99)`,
                        }}
                      />
                    </div>
                  </div>

                  {/* Hashtags */}
                  <div className="flex flex-wrap gap-1.5 mb-3">
                    {trend.hashtags.map((tag, j) => (
                      <span key={j} className="badge badge-platform text-[10px]">
                        <Hash size={10} className="mr-0.5" />
                        {tag.replace("#", "")}
                      </span>
                    ))}
                  </div>

                  {/* Footer */}
                  <div className="flex items-center justify-between text-xs" style={{ color: "var(--text-dim)" }}>
                    <div className="flex items-center gap-1.5">
                      {trend.platforms.map((p, j) => (
                        <span key={j} className={`platform-${p}`}>{p}</span>
                      ))}
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock size={12} />
                      Peak in {trend.peak_prediction_hours}h
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && searched && trends.length === 0 && !error && (
          <div className="text-center py-16">
            <TrendingUp size={48} className="mx-auto mb-4" style={{ color: "var(--text-dim)" }} />
            <p className="text-lg font-medium mb-2" style={{ color: "var(--text-muted)" }}>
              No trends found
            </p>
            <p className="text-sm" style={{ color: "var(--text-dim)" }}>
              Try a different topic or platform
            </p>
          </div>
        )}

        {/* Initial State */}
        {!loading && !searched && (
          <div className="text-center py-16 animate-fade-in">
            <div
              className="w-20 h-20 rounded-2xl mx-auto mb-5 flex items-center justify-center animate-pulse-glow"
              style={{
                background: "linear-gradient(135deg, rgba(124,58,237,0.15), rgba(6,182,212,0.1))",
                border: "1px solid rgba(124,58,237,0.2)",
              }}
            >
              <TrendingUp size={36} style={{ color: "var(--accent-light)" }} />
            </div>
            <h3 className="text-xl font-semibold mb-2">Discover What&apos;s Trending</h3>
            <p className="text-sm max-w-md mx-auto" style={{ color: "var(--text-muted)" }}>
              Enter a topic above and our AI agents will analyze real-time social media signals
              to find the hottest trends, hashtags, and content opportunities.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
