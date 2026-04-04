"use client";

import Sidebar from "@/components/Sidebar";
import {
  TrendingUp,
  Sparkles,
  Target,
  BarChart3,
  ArrowUpRight,
  Zap,
  Eye,
  Heart,
} from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

const statCards = [
  {
    label: "Trends Tracked",
    value: "2,847",
    change: "+12.5%",
    icon: TrendingUp,
    color: "#7c3aed",
    glow: "rgba(124,58,237,0.15)",
  },
  {
    label: "Content Generated",
    value: "384",
    change: "+24.1%",
    icon: Sparkles,
    color: "#06b6d4",
    glow: "rgba(6,182,212,0.15)",
  },
  {
    label: "Avg Virality Score",
    value: "78.3",
    change: "+8.2%",
    icon: BarChart3,
    color: "#10b981",
    glow: "rgba(16,185,129,0.15)",
  },
  {
    label: "Strategies Created",
    value: "156",
    change: "+15.7%",
    icon: Target,
    color: "#f59e0b",
    glow: "rgba(245,158,11,0.15)",
  },
];

const quickActions = [
  {
    title: "Discover Trends",
    desc: "Find what's going viral right now",
    href: "/trends",
    icon: TrendingUp,
    gradient: "linear-gradient(135deg, #7c3aed20, #a855f710)",
    border: "rgba(124,58,237,0.3)",
  },
  {
    title: "Content Studio",
    desc: "Generate AI-optimized content",
    href: "/content-studio",
    icon: Sparkles,
    gradient: "linear-gradient(135deg, #06b6d420, #0ea5e910)",
    border: "rgba(6,182,212,0.3)",
  },
  {
    title: "Build Strategy",
    desc: "7-day content calendar & plan",
    href: "/strategy",
    icon: Target,
    gradient: "linear-gradient(135deg, #10b98120, #059f6810)",
    border: "rgba(16,185,129,0.3)",
  },
];

const recentActivities = [
  { action: "Generated viral content for", topic: "AI Productivity Tools", platform: "Instagram", time: "2 min ago", icon: Sparkles },
  { action: "Discovered 8 trends about", topic: "Future of Remote Work", platform: "TikTok", time: "15 min ago", icon: TrendingUp },
  { action: "Created strategy for", topic: "Health & Fitness", platform: "YouTube", time: "1 hour ago", icon: Target },
  { action: "Predicted virality for", topic: "Tech Reviews", platform: "Twitter", time: "2 hours ago", icon: BarChart3 },
];

export default function Dashboard() {
  const [mounted, setMounted] = useState(false);
  const [user, setUser] = useState<string>("Creator");

  useEffect(() => {
    setMounted(true);
    try {
      const stored = localStorage.getItem("user");
      if (stored) {
        const parsed = JSON.parse(stored);
        setUser(parsed.full_name || parsed.username || "Creator");
      }
    } catch {}
  }, []);

  if (!mounted) return null;

  return (
    <div className="app-shell">
      <Sidebar />
      <main className="page-content">
        {/* Header */}
        <div className="page-hero animate-fade-in">
          <div className="hero-kicker">Control center</div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-2xl">👋</span>
            <h1 className="text-2xl md:text-4xl font-bold">
              Welcome back, <span className="gradient-text">{user}</span>
            </h1>
          </div>
          <p className="max-w-2xl mt-3" style={{ color: "var(--text-muted)" }}>
            Here&apos;s your content intelligence overview, with trend momentum, publishing tools, and strategy insights in one place.
          </p>
          <div className="status-strip mt-5">
            <div className="status-chip">Working dashboard shell on desktop and mobile</div>
            <div className="status-chip">Fast demo mode for trends, studio, and strategy</div>
            <div className="status-chip">Prepared for CI, Docker, and staged deployment</div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8 stagger-children">
          {statCards.map((card) => {
            const Icon = card.icon;
            return (
              <div
                key={card.label}
                className="glass-card p-5 group cursor-default"
              >
                <div className="flex items-start justify-between mb-3">
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-300 group-hover:scale-110"
                    style={{ background: card.glow }}
                  >
                    <Icon size={20} style={{ color: card.color }} />
                  </div>
                  <span
                    className="text-xs font-semibold px-2 py-1 rounded-full"
                    style={{
                      color: "#10b981",
                      background: "rgba(16,185,129,0.1)",
                    }}
                  >
                    {card.change}
                  </span>
                </div>
                <p
                  className="text-2xl font-bold mb-1"
                  style={{ color: card.color }}
                >
                  {card.value}
                </p>
                <p className="text-sm" style={{ color: "var(--text-muted)" }}>
                  {card.label}
                </p>
              </div>
            );
          })}
        </div>

        {/* Quick Actions */}
        <div className="mb-8 animate-fade-in-up" style={{ animationDelay: "0.2s" }}>
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Zap size={18} style={{ color: "var(--accent-light)" }} />
            Quick Actions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {quickActions.map((action) => {
              const Icon = action.icon;
              return (
                <Link key={action.href} href={action.href}>
                  <div
                    className="glass-card p-5 cursor-pointer group"
                    style={{
                      background: action.gradient,
                      borderColor: action.border,
                    }}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <Icon size={24} style={{ color: "var(--accent-light)" }} />
                      <ArrowUpRight
                        size={18}
                        className="opacity-0 group-hover:opacity-100 transition-opacity"
                        style={{ color: "var(--text-muted)" }}
                      />
                    </div>
                    <h3 className="font-semibold mb-1">{action.title}</h3>
                    <p className="text-sm" style={{ color: "var(--text-muted)" }}>
                      {action.desc}
                    </p>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>

        {/* Two Column: Activity + Live Stats */}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 animate-fade-in-up" style={{ animationDelay: "0.3s" }}>
          {/* Recent Activity */}
          <div className="lg:col-span-3 glass-card p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Eye size={18} style={{ color: "var(--accent-cyan)" }} />
              Recent Activity
            </h2>
            <div className="space-y-3">
              {recentActivities.map((activity, i) => {
                const Icon = activity.icon;
                return (
                  <div
                    key={i}
                    className="flex items-center gap-3 p-3 rounded-xl transition-colors hover:bg-white/5"
                    style={{ borderBottom: i < recentActivities.length - 1 ? "1px solid var(--border)" : "none" }}
                  >
                    <div
                      className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
                      style={{ background: "rgba(124,58,237,0.1)" }}
                    >
                      <Icon size={16} style={{ color: "var(--accent-light)" }} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm">
                        {activity.action}{" "}
                        <span className="font-semibold" style={{ color: "var(--accent-light)" }}>
                          {activity.topic}
                        </span>
                      </p>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="badge badge-platform text-[10px]">
                          {activity.platform}
                        </span>
                        <span className="text-[11px]" style={{ color: "var(--text-dim)" }}>
                          {activity.time}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Platform Pulse */}
          <div className="lg:col-span-2 glass-card p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Heart size={18} style={{ color: "#ef4444" }} />
              Platform Pulse
            </h2>
            <div className="space-y-4">
              {[
                { name: "Instagram", score: 87, color: "#E1306C" },
                { name: "TikTok", score: 94, color: "#00f2ea" },
                { name: "YouTube", score: 72, color: "#FF0000" },
                { name: "Twitter/X", score: 65, color: "#1DA1F2" },
                { name: "LinkedIn", score: 58, color: "#0077B5" },
              ].map((platform) => (
                <div key={platform.name}>
                  <div className="flex justify-between text-sm mb-1.5">
                    <span style={{ color: "var(--text-muted)" }}>{platform.name}</span>
                    <span className="font-semibold" style={{ color: platform.color }}>
                      {platform.score}%
                    </span>
                  </div>
                  <div
                    className="h-2 rounded-full overflow-hidden"
                    style={{ background: "var(--bg-secondary)" }}
                  >
                    <div
                      className="h-full rounded-full transition-all duration-1000"
                      style={{
                        width: `${platform.score}%`,
                        background: `linear-gradient(90deg, ${platform.color}, ${platform.color}99)`,
                        boxShadow: `0 0 8px ${platform.color}40`,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
            <p className="text-[11px] mt-4" style={{ color: "var(--text-dim)" }}>
              Trending activity score — updated in real-time
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}

//app/page.tsx