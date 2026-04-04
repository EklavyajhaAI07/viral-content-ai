"use client";

import Sidebar from "@/components/Sidebar";
import ScoreGauge from "@/components/ScoreGauge";
import { contentAPI, getApiErrorMessage } from "@/lib/api";
import type { HookResponse, CaptionResponse, HashtagResponse, ViralityResponse, ThumbnailResponse } from "@/types";
import {
  Sparkles, Loader2, AlertCircle, Copy, Check,
  Hash, Lightbulb, Clock, FileText, Zap,
  ArrowRight, Image as ImageIcon, BarChart3, Download,
} from "lucide-react";
import { useState } from "react";

const platforms = ["instagram", "tiktok", "youtube", "linkedin", "twitter"];
const tones = ["engaging", "professional", "casual", "humorous", "inspiring", "educational"];

// ── Demo fallbacks ────────────────────────────────────────────────────────────

function demoHook(topic: string, platform: string): HookResponse {
  return {
    job_id: "demo", topic, platform,
    hook: `You won't believe what's happening with ${topic}...`,
    alternative_hooks: [
      `The truth about ${topic} nobody tells you`,
      `I tried ${topic} for 30 days — here's what changed`,
      `Stop doing ${topic} wrong. Here's why:`,
    ],
    cta: "Save this and share it with someone who needs it!",
    format_recommendation: "Reel",
    status: "demo", cached: false, elapsed_seconds: 0,
  };
}

function demoCaption(topic: string, platform: string): CaptionResponse {
  return {
    job_id: "demo", topic, platform,
    caption: `🔥 Everything about ${topic} is changing right now.\n\nMost people are still doing it the old way — and falling behind.\n\nHere's the thing nobody's talking about: the creators winning in 2025 all shifted their approach early.\n\nAre you still stuck on the old playbook? Drop a 💬 below and tell me where you're at.\n\n#${topic.replace(/\s+/g, "")} #ContentStrategy #CreatorTips`,
    best_posting_time: "Tuesday–Thursday, 7–9 PM",
    word_count: 68,
    status: "demo", cached: false, elapsed_seconds: 0,
  };
}

function demoHashtags(topic: string, platform: string): HashtagResponse {
  const slug = topic.toLowerCase().replace(/\s+/g, "");
  return {
    job_id: "demo", topic, platform,
    niche: [`#${slug}Tips`, `#${slug}Life`, `#${slug}Hack`, `#${slug}Daily`, `#${slug}101`],
    trending: [`#${slug}`, `#${platform}${slug.charAt(0).toUpperCase() + slug.slice(1)}`, "#ContentCreator2025", "#ViralContent", "#TrendingNow"],
    broad: ["#viral", "#explore", "#reels", "#trending", "#fyp"],
    total_count: 15,
    status: "demo", cached: false, elapsed_seconds: 0,
  };
}

function demoVirality(topic: string, platform: string): ViralityResponse {
  return {
    job_id: "demo", topic, platform,
    overall_score: 74, grade: "B+", confidence: 0.78,
    predicted_reach: 42000, predicted_engagement_rate: 4.1,
    breakdown: { hook_strength: 78, hashtag_relevance: 70, trend_alignment: 80, emotional_tone: 72, posting_time_fit: 68 },
    improvements: [
      "Start with a direct question to boost comment rate",
      "Add 3 niche hashtags under 500k posts for better reach",
      "Post Tuesday–Thursday between 7–9 PM for peak engagement",
    ],
    rewritten_hook: `Here's the ${topic} mistake everyone keeps making (and how to fix it fast)`,
    status: "demo", cached: false, elapsed_seconds: 0,
  };
}

function demoThumbnail(topic: string, platform: string): ThumbnailResponse {
  return {
    job_id: "demo", topic, platform,
    thumbnail: {
      url: `https://picsum.photos/seed/${topic.replace(/\s/g, "")}/800/450`,
      path: "",
      status: "ok",
      source: "demo",
    },
    status: "demo", cached: false, elapsed_seconds: 0,
  };
}

// ── Component ─────────────────────────────────────────────────────────────────

type Tab = "hook" | "caption" | "hashtags" | "virality" | "thumbnail";

export default function ContentStudioPage() {
  const [topic, setTopic] = useState("");
  const [platform, setPlatform] = useState("instagram");
  const [tone, setTone] = useState("engaging");
  const [audience, setAudience] = useState("");

  const [hook, setHook] = useState<HookResponse | null>(null);
  const [caption, setCaption] = useState<CaptionResponse | null>(null);
  const [hashtags, setHashtags] = useState<HashtagResponse | null>(null);
  const [virality, setVirality] = useState<ViralityResponse | null>(null);
  const [thumbnail, setThumbnail] = useState<ThumbnailResponse | null>(null);

  const [activeTab, setActiveTab] = useState<Tab>("hook");
  const [loadingTab, setLoadingTab] = useState<Tab | null>(null);
  const [errors, setErrors] = useState<Partial<Record<Tab, string>>>({});
  const [isDemo, setIsDemo] = useState(false);
  const [copiedField, setCopiedField] = useState("");

  const copy = (text: string, field: string) => {
    navigator.clipboard.writeText(text);
    setCopiedField(field);
    setTimeout(() => setCopiedField(""), 2000);
  };

  const CopyBtn = ({ text, field }: { text: string; field: string }) => (
    <button onClick={() => copy(text, field)} className="p-1.5 rounded-lg hover:bg-white/10" title="Copy">
      {copiedField === field
        ? <Check size={14} style={{ color: "var(--success)" }} />
        : <Copy size={14} style={{ color: "var(--text-dim)" }} />}
    </button>
  );

  const generateHook = async () => {
    if (!topic.trim()) return;
    setLoadingTab("hook");
    setActiveTab("hook");
    setErrors(e => ({ ...e, hook: "" }));
    try {
      const res = await contentAPI.generateHook({ topic: topic.trim(), platform, tone, target_audience: audience || "general" });
      setHook(res); setIsDemo(false);
    } catch (err) {
      setHook(demoHook(topic.trim(), platform)); setIsDemo(true);
      setErrors(e => ({ ...e, hook: getApiErrorMessage(err, "Backend unavailable — demo shown") }));
    } finally { setLoadingTab(null); }
  };

  const generateCaption = async () => {
    if (!topic.trim()) return;
    setLoadingTab("caption");
    setActiveTab("caption");
    setErrors(e => ({ ...e, caption: "" }));
    try {
      const res = await contentAPI.generateCaption({ topic: topic.trim(), platform, tone, target_audience: audience || "general", hook: hook?.hook });
      setCaption(res); setIsDemo(false);
    } catch (err) {
      setCaption(demoCaption(topic.trim(), platform)); setIsDemo(true);
      setErrors(e => ({ ...e, caption: getApiErrorMessage(err, "Backend unavailable — demo shown") }));
    } finally { setLoadingTab(null); }
  };

  const generateHashtags = async () => {
    if (!topic.trim()) return;
    setLoadingTab("hashtags");
    setActiveTab("hashtags");
    setErrors(e => ({ ...e, hashtags: "" }));
    try {
      const res = await contentAPI.generateHashtags({ topic: topic.trim(), platform });
      setHashtags(res); setIsDemo(false);
    } catch (err) {
      setHashtags(demoHashtags(topic.trim(), platform)); setIsDemo(true);
      setErrors(e => ({ ...e, hashtags: getApiErrorMessage(err, "Backend unavailable — demo shown") }));
    } finally { setLoadingTab(null); }
  };

  const predictVirality = async () => {
    if (!topic.trim()) return;
    setLoadingTab("virality");
    setActiveTab("virality");
    setErrors(e => ({ ...e, virality: "" }));
    try {
      const allHashtags = hashtags ? [...hashtags.niche, ...hashtags.trending, ...hashtags.broad].join(" ") : "";
      const res = await contentAPI.predictVirality({ topic: topic.trim(), platform, caption: caption?.caption, hashtags: allHashtags });
      setVirality(res); setIsDemo(false);
    } catch (err) {
      setVirality(demoVirality(topic.trim(), platform)); setIsDemo(true);
      setErrors(e => ({ ...e, virality: getApiErrorMessage(err, "Backend unavailable — demo shown") }));
    } finally { setLoadingTab(null); }
  };

  const generateThumbnail = async () => {
    if (!topic.trim()) return;
    setLoadingTab("thumbnail");
    setActiveTab("thumbnail");
    setErrors(e => ({ ...e, thumbnail: "" }));
    try {
      const res = await contentAPI.generateThumbnail({ topic: topic.trim(), platform, tone });
      setThumbnail(res); setIsDemo(false);
    } catch (err) {
      setThumbnail(demoThumbnail(topic.trim(), platform)); setIsDemo(true);
      setErrors(e => ({ ...e, thumbnail: getApiErrorMessage(err, "Backend unavailable — demo shown") }));
    } finally { setLoadingTab(null); }
  };

  const tabs: { id: Tab; label: string; icon: React.ReactNode; action: () => void; ready: boolean }[] = [
    { id: "hook",      label: "Hook",      icon: <Zap size={15} />,        action: generateHook,      ready: !!hook },
    { id: "caption",   label: "Caption",   icon: <FileText size={15} />,    action: generateCaption,   ready: !!caption },
    { id: "hashtags",  label: "Hashtags",  icon: <Hash size={15} />,        action: generateHashtags,  ready: !!hashtags },
    { id: "virality",  label: "Virality",  icon: <BarChart3 size={15} />,   action: predictVirality,   ready: !!virality },
    { id: "thumbnail", label: "Thumbnail", icon: <ImageIcon size={15} />,   action: generateThumbnail, ready: !!thumbnail },
  ];

  const isLoading = loadingTab !== null;

  // Aspect ratio class based on platform
  const thumbnailAspect = platform === "youtube"
    ? "aspect-video"
    : platform === "instagram" || platform === "tiktok"
      ? "aspect-[9/16] max-h-[500px]"
      : "aspect-square";

  return (
    <div className="app-shell">
      <Sidebar />
      <main className="page-content">

        {/* ── Hero ────────────────────────────────────────────── */}
        <div className="page-hero animate-fade-in">
          <div className="hero-kicker">Content lab</div>
          <h1 className="text-2xl md:text-4xl font-bold flex items-center gap-3">
            <Sparkles size={28} style={{ color: "var(--accent-light)" }} /> Content Studio
          </h1>
          <p className="mt-3 max-w-2xl" style={{ color: "var(--text-muted)" }}>
            Run each AI agent independently — generate your hook, caption, hashtags, virality score, and thumbnail one at a time.
          </p>
          <div className="status-strip mt-5">
            <div className="status-chip">1 button = 1 agent = 1 focused result</div>
            <div className="status-chip">Chain outputs for better accuracy</div>
            <div className="status-chip">AI thumbnail generation included</div>
          </div>
        </div>

        {/* ── Input Form ──────────────────────────────────────── */}
        <div className="glass-card p-6 mb-6 animate-fade-in-up">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="text-sm font-medium mb-2 block" style={{ color: "var(--text-muted)" }}>Topic *</label>
              <input className="input-field" placeholder="e.g., 5 AI tools replacing jobs in 2026"
                value={topic} onChange={e => setTopic(e.target.value)} />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block" style={{ color: "var(--text-muted)" }}>Target Audience</label>
              <input className="input-field" placeholder="e.g., Entrepreneurs, Gen Z"
                value={audience} onChange={e => setAudience(e.target.value)} />
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-5">
            <div>
              <label className="text-sm font-medium mb-2 block" style={{ color: "var(--text-muted)" }}>Platform</label>
              <select className="input-field" value={platform} onChange={e => setPlatform(e.target.value)}>
                {platforms.map(p => <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>)}
              </select>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block" style={{ color: "var(--text-muted)" }}>Tone</label>
              <select className="input-field" value={tone} onChange={e => setTone(e.target.value)}>
                {tones.map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
              </select>
            </div>
          </div>

          {/* ── 5 Agent Buttons ─────────────────────────────── */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => { tab.action(); }}
                disabled={isLoading || !topic.trim()}
                className={`flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-semibold transition-all duration-200 ${
                  tab.ready ? "btn-primary" : "btn-secondary"
                }`}
              >
                {loadingTab === tab.id
                  ? <><Loader2 size={15} className="animate-spin" /> Running...</>
                  : <>{tab.icon} {tab.ready ? `Re-run ${tab.label}` : `Generate ${tab.label}`}</>}
              </button>
            ))}
          </div>

          {isDemo && (
            <p className="text-xs mt-3 px-1" style={{ color: "var(--warning)" }}>
              ⚠ Demo mode — connect backend for live AI results.
            </p>
          )}
        </div>

        {/* ── Tabs ────────────────────────────────────────────── */}
        {(hook || caption || hashtags || virality || thumbnail || loadingTab !== null) && (
          <div className="animate-fade-in-up">

            {/* Tab bar */}
            <div className="flex gap-2 mb-4 border-b pb-2 overflow-x-auto" style={{ borderColor: "var(--border)" }}>
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-1.5 px-4 py-2 rounded-t-xl text-sm font-medium transition-all whitespace-nowrap ${
                    activeTab === tab.id ? "border-b-2" : "opacity-50 hover:opacity-80"
                  }`}
                  style={{
                    color: activeTab === tab.id ? "var(--accent-light)" : "var(--text-muted)",
                    borderColor: activeTab === tab.id ? "var(--accent-light)" : "transparent",
                  }}
                >
                  {tab.icon} {tab.label}
                  {tab.ready && <span className="w-1.5 h-1.5 rounded-full ml-1" style={{ background: "var(--success)" }} />}
                </button>
              ))}
            </div>

            {/* ── Hook Tab ──────────────────────────────────── */}
            {activeTab === "hook" && hook && (
              <div className="space-y-4">
                {errors.hook && <ErrorBanner msg={errors.hook} />}
                <div className="glass-card p-5">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold flex items-center gap-2"><Zap size={16} style={{ color: "var(--warning)" }} /> Best Hook</h3>
                    <CopyBtn text={hook.hook} field="hook" />
                  </div>
                  <p className="text-lg font-medium" style={{ color: "var(--accent-light)" }}>{hook.hook}</p>
                </div>
                <div className="glass-card p-5">
                  <h3 className="font-semibold flex items-center gap-2 mb-3"><Lightbulb size={16} style={{ color: "var(--warning)" }} /> Alternative Hooks</h3>
                  <ul className="space-y-2">
                    {hook.alternative_hooks.map((h, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm" style={{ color: "var(--text-muted)" }}>
                        <ArrowRight size={14} className="mt-0.5 flex-shrink-0" style={{ color: "var(--accent-light)" }} />{h}
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="glass-card p-4">
                    <p className="text-xs mb-1" style={{ color: "var(--text-dim)" }}>CTA</p>
                    <p className="text-sm" style={{ color: "var(--text-muted)" }}>{hook.cta}</p>
                  </div>
                  <div className="glass-card p-4">
                    <p className="text-xs mb-1" style={{ color: "var(--text-dim)" }}>Recommended Format</p>
                    <p className="text-sm font-semibold">{hook.format_recommendation}</p>
                  </div>
                </div>
                <p className="text-xs px-1" style={{ color: "var(--text-dim)" }}>
                  💡 Tip: Now click <strong>Generate Caption</strong> — it will use this hook automatically.
                </p>
              </div>
            )}

            {/* ── Caption Tab ───────────────────────────────── */}
            {activeTab === "caption" && caption && (
              <div className="space-y-4">
                {errors.caption && <ErrorBanner msg={errors.caption} />}
                <div className="glass-card p-5">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold flex items-center gap-2"><FileText size={16} style={{ color: "var(--accent-cyan)" }} /> Full Caption</h3>
                    <CopyBtn text={caption.caption} field="caption" />
                  </div>
                  <p className="text-sm whitespace-pre-line" style={{ color: "var(--text-muted)" }}>{caption.caption}</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="glass-card p-4">
                    <p className="text-xs mb-1" style={{ color: "var(--text-dim)" }}>Best Posting Time</p>
                    <p className="font-semibold flex items-center gap-1.5"><Clock size={14} style={{ color: "var(--accent-cyan)" }} />{caption.best_posting_time}</p>
                  </div>
                  <div className="glass-card p-4">
                    <p className="text-xs mb-1" style={{ color: "var(--text-dim)" }}>Word Count</p>
                    <p className="font-semibold">{caption.word_count} words</p>
                  </div>
                </div>
                <p className="text-xs px-1" style={{ color: "var(--text-dim)" }}>
                  💡 Tip: Now click <strong>Generate Hashtags</strong>, then <strong>Predict Virality</strong> for the most accurate score.
                </p>
              </div>
            )}

            {/* ── Hashtags Tab ──────────────────────────────── */}
            {activeTab === "hashtags" && hashtags && (
              <div className="space-y-4">
                {errors.hashtags && <ErrorBanner msg={errors.hashtags} />}
                {(["niche", "trending", "broad"] as const).map(tier => (
                  <div key={tier} className="glass-card p-5">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold flex items-center gap-2">
                        <Hash size={16} style={{ color: tier === "niche" ? "var(--success)" : tier === "trending" ? "var(--accent-light)" : "var(--accent-cyan)" }} />
                        {tier.charAt(0).toUpperCase() + tier.slice(1)} Hashtags
                        <span className="text-xs font-normal" style={{ color: "var(--text-dim)" }}>
                          {tier === "niche" ? "(< 500k posts)" : tier === "trending" ? "(500k – 5M posts)" : "(5M+ posts)"}
                        </span>
                      </h3>
                      <CopyBtn text={hashtags[tier].join(" ")} field={tier} />
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {hashtags[tier].map((tag, i) => (
                        <span key={i} className="badge badge-platform text-xs">{tag}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* ── Virality Tab ──────────────────────────────── */}
            {activeTab === "virality" && virality && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {errors.virality && <div className="lg:col-span-3"><ErrorBanner msg={errors.virality} /></div>}
                <div className="glass-card p-6 flex flex-col items-center">
                  <ScoreGauge score={virality.overall_score} grade={virality.grade} size={180} />
                  <p className="text-sm mt-4" style={{ color: "var(--text-muted)" }}>
                    Confidence: <span className="font-semibold">{(virality.confidence * 100).toFixed(0)}%</span>
                  </p>
                  <div className="grid grid-cols-2 gap-3 w-full mt-4">
                    <div className="p-3 rounded-xl text-center" style={{ background: "var(--bg-secondary)" }}>
                      <p className="text-xs mb-1" style={{ color: "var(--text-dim)" }}>Reach</p>
                      <p className="text-lg font-bold" style={{ color: "var(--accent-light)" }}>
                        {virality.predicted_reach >= 1000 ? `${(virality.predicted_reach / 1000).toFixed(1)}K` : virality.predicted_reach}
                      </p>
                    </div>
                    <div className="p-3 rounded-xl text-center" style={{ background: "var(--bg-secondary)" }}>
                      <p className="text-xs mb-1" style={{ color: "var(--text-dim)" }}>Engagement</p>
                      <p className="text-lg font-bold" style={{ color: "var(--success)" }}>{virality.predicted_engagement_rate}%</p>
                    </div>
                  </div>
                </div>
                <div className="glass-card p-5">
                  <h3 className="font-semibold text-sm mb-3">Score Breakdown</h3>
                  <div className="space-y-2.5">
                    {Object.entries(virality.breakdown).map(([k, v]) => (
                      <div key={k}>
                        <div className="flex justify-between text-xs mb-1">
                          <span style={{ color: "var(--text-muted)" }}>{k.split("_").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ")}</span>
                          <span className="font-semibold">{v}</span>
                        </div>
                        <div className="h-1.5 rounded-full" style={{ background: "var(--bg-secondary)" }}>
                          <div className="h-full rounded-full" style={{ width: `${v}%`, background: v >= 70 ? "#10b981" : v >= 50 ? "#f59e0b" : "#ef4444" }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="space-y-4">
                  <div className="glass-card p-5">
                    <h3 className="font-semibold text-sm mb-3 flex items-center gap-2">
                      <Lightbulb size={14} style={{ color: "var(--warning)" }} /> Improvements
                    </h3>
                    <ul className="space-y-2">
                      {virality.improvements.map((t, i) => (
                        <li key={i} className="flex items-start gap-2 text-xs" style={{ color: "var(--text-muted)" }}>
                          <span className="font-bold" style={{ color: "var(--accent-light)" }}>{i + 1}.</span>{t}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="glass-card p-5">
                    <h3 className="font-semibold text-sm mb-2 flex items-center gap-2">
                      <Zap size={14} style={{ color: "var(--accent-cyan)" }} /> Rewritten Hook
                    </h3>
                    <p className="text-sm italic" style={{ color: "var(--accent-light)" }}>&ldquo;{virality.rewritten_hook}&rdquo;</p>
                  </div>
                </div>
              </div>
            )}

            {/* ── Thumbnail Tab ─────────────────────────────── */}
            {activeTab === "thumbnail" && thumbnail && (
              <div className="space-y-4">
                {errors.thumbnail && <ErrorBanner msg={errors.thumbnail} />}

                <div className="glass-card p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold flex items-center gap-2">
                      <ImageIcon size={16} style={{ color: "var(--accent-cyan)" }} />
                      Generated Thumbnail
                    </h3>
                    <div className="flex items-center gap-2">
                      {/* Source badge */}
                      <span className="text-xs px-2 py-1 rounded-full font-medium capitalize"
                        style={{ background: "rgba(6,182,212,0.15)", color: "var(--accent-cyan)", border: "1px solid rgba(6,182,212,0.3)" }}>
                        {thumbnail.thumbnail?.source ?? "ai"}
                      </span>
                      {/* Download button */}
                      {thumbnail.thumbnail?.url && (
                        <a
                          href={thumbnail.thumbnail.url}
                          download={`thumbnail-${topic.replace(/\s+/g, "-")}.png`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all"
                          style={{ background: "rgba(124,58,237,0.2)", color: "var(--accent-light)", border: "1px solid rgba(124,58,237,0.3)" }}
                        >
                          <Download size={13} /> Download
                        </a>
                      )}
                    </div>
                  </div>

                  {/* Thumbnail image — aspect ratio matches platform */}
                  <div className={`relative w-full overflow-hidden rounded-xl mx-auto ${thumbnailAspect}`}
                    style={{
                      maxWidth: platform === "instagram" || platform === "tiktok" ? "280px" : "100%",
                      background: "var(--bg-secondary)",
                      border: "1px solid var(--border)",
                    }}>
                    {thumbnail.thumbnail?.url ? (
                      <img
                        src={thumbnail.thumbnail.url}
                        alt={`Thumbnail for ${topic}`}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = `https://picsum.photos/seed/${topic}/800/450`;
                        }}
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <ImageIcon size={48} style={{ color: "var(--text-dim)" }} />
                      </div>
                    )}
                  </div>

                  {/* Meta info */}
                  <div className="grid grid-cols-3 gap-3 mt-4">
                    <div className="p-3 rounded-xl text-center" style={{ background: "var(--bg-secondary)" }}>
                      <p className="text-xs mb-1" style={{ color: "var(--text-dim)" }}>Platform</p>
                      <p className="text-sm font-semibold capitalize">{platform}</p>
                    </div>
                    <div className="p-3 rounded-xl text-center" style={{ background: "var(--bg-secondary)" }}>
                      <p className="text-xs mb-1" style={{ color: "var(--text-dim)" }}>Aspect Ratio</p>
                      <p className="text-sm font-semibold">
                        {platform === "youtube" ? "16:9" : platform === "instagram" || platform === "tiktok" ? "9:16" : "1:1"}
                      </p>
                    </div>
                    <div className="p-3 rounded-xl text-center" style={{ background: "var(--bg-secondary)" }}>
                      <p className="text-xs mb-1" style={{ color: "var(--text-dim)" }}>Status</p>
                      <p className="text-sm font-semibold" style={{ color: thumbnail.thumbnail?.status === "ok" ? "var(--success)" : "var(--warning)" }}>
                        {thumbnail.thumbnail?.status === "ok" ? "✓ Ready" : "Pending"}
                      </p>
                    </div>
                  </div>
                </div>

                <p className="text-xs px-1" style={{ color: "var(--text-dim)" }}>
                  💡 Tip: Thumbnail is AI-generated using Stability AI with Pollinations FLUX as fallback. Re-run to get a different variation.
                </p>
              </div>
            )}

            {/* Tab placeholders when tab not yet run */}
            {activeTab === "hook"      && !hook      && <TabPlaceholder label="Hook"          action={generateHook}      loading={loadingTab === "hook"} />}
            {activeTab === "caption"   && !caption   && <TabPlaceholder label="Caption"       action={generateCaption}   loading={loadingTab === "caption"} />}
            {activeTab === "hashtags"  && !hashtags  && <TabPlaceholder label="Hashtags"      action={generateHashtags}  loading={loadingTab === "hashtags"} />}
            {activeTab === "virality"  && !virality  && <TabPlaceholder label="Virality Score" action={predictVirality}   loading={loadingTab === "virality"} />}
            {activeTab === "thumbnail" && !thumbnail && <TabPlaceholder label="Thumbnail"     action={generateThumbnail} loading={loadingTab === "thumbnail"} />}
          </div>
        )}

        {/* ── Initial Empty State ──────────────────────────────── */}
        {!hook && !caption && !hashtags && !virality && !thumbnail && loadingTab === null && (
          <div className="text-center py-16 animate-fade-in">
            <div className="w-20 h-20 rounded-2xl mx-auto mb-5 flex items-center justify-center animate-pulse-glow"
              style={{ background: "linear-gradient(135deg, rgba(6,182,212,0.15), rgba(124,58,237,0.1))", border: "1px solid rgba(6,182,212,0.2)" }}>
              <Sparkles size={36} style={{ color: "var(--accent-cyan)" }} />
            </div>
            <h3 className="text-xl font-semibold mb-2">AI Content Studio</h3>
            <p className="text-sm max-w-lg mx-auto" style={{ color: "var(--text-muted)" }}>
              Enter your topic, then run each agent independently. Start with <strong>Generate Hook</strong> → chain through to <strong>Predict Virality</strong>, then generate a <strong>Thumbnail</strong> to complete your content package.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}

// ── Small helpers ─────────────────────────────────────────────────────────────

function ErrorBanner({ msg }: { msg: string }) {
  return (
    <div className="flex items-center gap-3 p-4 rounded-xl mb-2"
      style={{ background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)" }}>
      <AlertCircle size={16} style={{ color: "#ef4444" }} />
      <p className="text-xs" style={{ color: "#ef4444" }}>{msg}</p>
    </div>
  );
}

function TabPlaceholder({ label, action, loading }: { label: string; action: () => void; loading: boolean }) {
  return (
    <div className="text-center py-12 glass-card">
      <p className="text-sm mb-4" style={{ color: "var(--text-muted)" }}>No {label} generated yet.</p>
      <button className="btn-secondary" onClick={action} disabled={loading}>
        {loading ? <><Loader2 size={14} className="animate-spin" /> Running...</> : <>Generate {label}</>}
      </button>
    </div>
  );
}