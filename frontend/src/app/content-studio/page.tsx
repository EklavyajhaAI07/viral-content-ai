"use client";

import Sidebar from "@/components/Sidebar";
import ScoreGauge from "@/components/ScoreGauge";
import {
  generateDemoContent,
  generateDemoVirality,
} from "@/lib/demoData";
import { contentAPI, getApiErrorMessage } from "@/lib/api";
import { ContentData, ViralityData } from "@/types";
import {
  Sparkles, Loader2, AlertCircle, Copy, Check, Hash,
  Lightbulb, Clock, FileText, Zap, ArrowRight, Image as ImageIcon
} from "lucide-react";
import { useState } from "react";

const platforms = ["instagram", "tiktok", "youtube", "linkedin", "twitter"];
const tones = ["engaging", "professional", "casual", "humorous", "inspiring", "educational"];

export default function ContentStudioPage() {
  const [topic, setTopic] = useState("");
  const [platform, setPlatform] = useState("instagram");
  const [tone, setTone] = useState("engaging");
  const [audience, setAudience] = useState("");
  const [content, setContent] = useState<ContentData | null>(null);
  const [virality, setVirality] = useState<ViralityData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copiedField, setCopiedField] = useState("");
  const [source, setSource] = useState("idle");

  const handleGenerate = async () => {
    if (!topic.trim()) return;
    setLoading(true); setError(""); setContent(null); setVirality(null); setSource("idle");
    try {
      const [cRes, vRes] = await Promise.allSettled([
        contentAPI.generate({ topic: topic.trim(), platform, tone, target_audience: audience || "general" }),
        contentAPI.predictVirality({ topic: topic.trim(), platform }),
      ]);
      if (cRes.status === "fulfilled") {
        setContent(cRes.value.data as unknown as ContentData);
      } else {
        setContent(generateDemoContent(topic.trim(), platform, tone, audience || "general"));
      }

      if (vRes.status === "fulfilled") {
        setVirality(vRes.value.data as unknown as ViralityData);
      } else {
        setVirality(generateDemoVirality(topic.trim(), platform));
      }

      if (cRes.status === "rejected" || vRes.status === "rejected") {
        setSource("offline_demo");
        setError("Backend is unavailable, so demo content and scoring are shown locally.");
      } else {
        setSource("api");
      }
    } catch (err: unknown) { setError(getApiErrorMessage(err, "Something went wrong")); }
    finally { setLoading(false); }
  };

  const copy = (text: string, f: string) => { navigator.clipboard.writeText(text); setCopiedField(f); setTimeout(() => setCopiedField(""), 2000); };
  const CopyBtn = ({ text, field }: { text: string; field: string }) => (
    <button onClick={() => copy(text, field)} className="p-1.5 rounded-lg hover:bg-white/10" title="Copy">
      {copiedField === field ? <Check size={14} style={{ color: "var(--success)" }} /> : <Copy size={14} style={{ color: "var(--text-dim)" }} />}
    </button>
  );

  return (
    <div className="app-shell">
      <Sidebar />
      <main className="page-content">
        <div className="page-hero animate-fade-in">
          <div className="hero-kicker">Content lab</div>
          <h1 className="text-2xl md:text-4xl font-bold flex items-center gap-3">
            <Sparkles size={28} style={{ color: "var(--accent-light)" }} /> Content Studio
          </h1>
          <p className="mt-3 max-w-2xl" style={{ color: "var(--text-muted)" }}>Generate AI-optimized content and predict virality before you post.</p>
          <div className="status-strip mt-5">
            <div className="status-chip">Topic-aware hooks and captions</div>
            <div className="status-chip">Tiered hashtag recommendations</div>
            <div className="status-chip">Reach and engagement forecast</div>
          </div>
        </div>

        {/* Input Form */}
        <div className="glass-card p-6 mb-6 animate-fade-in-up">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div><label className="text-sm font-medium mb-2 block" style={{ color: "var(--text-muted)" }}>Topic *</label>
              <input className="input-field" placeholder="e.g., 5 AI tools replacing jobs in 2026" value={topic} onChange={e => setTopic(e.target.value)} onKeyDown={e => e.key === "Enter" && handleGenerate()} /></div>
            <div><label className="text-sm font-medium mb-2 block" style={{ color: "var(--text-muted)" }}>Target Audience</label>
              <input className="input-field" placeholder="e.g., Entrepreneurs, Gen Z" value={audience} onChange={e => setAudience(e.target.value)} /></div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div><label className="text-sm font-medium mb-2 block" style={{ color: "var(--text-muted)" }}>Platform</label>
              <select className="input-field" value={platform} onChange={e => setPlatform(e.target.value)}>
                {platforms.map(p => <option key={p} value={p}>{p.charAt(0).toUpperCase()+p.slice(1)}</option>)}</select></div>
            <div><label className="text-sm font-medium mb-2 block" style={{ color: "var(--text-muted)" }}>Tone</label>
              <select className="input-field" value={tone} onChange={e => setTone(e.target.value)}>
                {tones.map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase()+t.slice(1)}</option>)}</select></div>
            <div className="flex items-end">
              <button className="btn-primary w-full" onClick={handleGenerate} disabled={loading || !topic.trim()}>
                {loading ? <><Loader2 size={16} className="animate-spin" /> Generating...</> : <><Zap size={16} /> Generate &amp; Predict</>}
              </button></div>
          </div>
        </div>

        {error && <div className="flex items-center gap-3 p-4 rounded-xl mb-6" style={{ background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)" }}>
          <AlertCircle size={18} style={{ color: "#ef4444" }} /><p className="text-sm" style={{ color: "#ef4444" }}>{error}</p></div>}

        {source !== "idle" && (
          <div className="source-banner mb-6">
            <span className="badge badge-platform">
              {source === "offline_demo" ? "Offline demo" : "api"}
            </span>
            <p>
              {source === "offline_demo"
                ? "The studio is still working with local fallback content and scoring."
                : "Content and scoring were returned by the backend flow."}
            </p>
          </div>
        )}

        {loading && <div className="grid grid-cols-1 lg:grid-cols-3 gap-6"><div className="lg:col-span-2 glass-card p-6"><div className="skeleton h-6 w-40 mb-4" /><div className="skeleton h-4 w-full mb-2" /><div className="skeleton h-4 w-3/4 mb-6" /><div className="skeleton h-32 w-full" /></div>
          <div className="glass-card p-6 flex items-center justify-center"><div className="skeleton rounded-full" style={{ width: 160, height: 160 }} /></div></div>}

        {!loading && (content || virality) && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in-up">
            {content && <div className="lg:col-span-2 space-y-4">
              
              {/* --- THUMBNAIL VIEWER ADDED HERE --- */}
              {content.thumbnail?.url && (
                <div className="glass-card p-5 relative overflow-hidden">
                  <h3 className="font-semibold flex items-center gap-2 mb-3">
                    <ImageIcon size={16} style={{ color: "var(--accent-light)" }} /> 
                    AI Generated Thumbnail
                  </h3>
                  <div className="relative w-full aspect-video md:aspect-[16/9] rounded-xl overflow-hidden" style={{ border: "1px solid var(--border)" }}>
                    <img 
                      src={content.thumbnail.url} 
                      alt="AI Thumbnail" 
                      className="object-cover w-full h-full"
                    />
                    <div className="absolute bottom-3 right-3 px-2 py-1 rounded bg-black/70 backdrop-blur text-[10px] uppercase tracking-wider text-white border border-white/10">
                      Generated via {content.thumbnail.source || "AI"}
                    </div>
                  </div>
                </div>
              )}
              {/* --------------------------------- */}

              <div className="glass-card p-5"><div className="flex items-center justify-between mb-3"><h3 className="font-semibold flex items-center gap-2"><Zap size={16} style={{ color: "var(--warning)" }} /> Hook</h3><CopyBtn text={content.hook} field="hook" /></div>
                <p className="text-lg font-medium" style={{ color: "var(--accent-light)" }}>{content.hook}</p></div>
              <div className="glass-card p-5"><div className="flex items-center justify-between mb-3"><h3 className="font-semibold flex items-center gap-2"><FileText size={16} style={{ color: "var(--accent-cyan)" }} /> Caption</h3><CopyBtn text={content.caption} field="caption" /></div>
                <p className="text-sm whitespace-pre-line" style={{ color: "var(--text-muted)" }}>{content.caption}</p></div>
              <div className="glass-card p-5"><h3 className="font-semibold flex items-center gap-2 mb-3"><Hash size={16} style={{ color: "var(--success)" }} /> Hashtags</h3>
                {content.hashtags && typeof content.hashtags === "object" && !Array.isArray(content.hashtags) ? (
                  <div className="space-y-3">{Object.entries(content.hashtags).map(([tier, tags]) => (
                    <div key={tier}><p className="text-xs font-semibold uppercase mb-1" style={{ color: "var(--text-dim)" }}>{tier}</p>
                      <div className="flex flex-wrap gap-1.5">{(tags as string[]).map((tag, j) => <span key={j} className="badge badge-platform text-[11px]">{tag}</span>)}</div></div>))}</div>
                ) : <div className="flex flex-wrap gap-1.5">{(Array.isArray(content.hashtags) ? content.hashtags : []).map((t, j) => <span key={j} className="badge badge-platform text-[11px]">{t}</span>)}</div>}</div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="glass-card p-5"><h3 className="font-semibold flex items-center gap-2 mb-3"><Lightbulb size={16} style={{ color: "var(--warning)" }} /> Alt Hooks</h3>
                  <ul className="space-y-2">{content.alternative_hooks?.map((h, i) => <li key={i} className="flex items-start gap-2 text-sm" style={{ color: "var(--text-muted)" }}><ArrowRight size={14} className="mt-0.5 flex-shrink-0" style={{ color: "var(--accent-light)" }} />{h}</li>)}</ul></div>
                <div className="glass-card p-5"><h3 className="font-semibold flex items-center gap-2 mb-3"><Clock size={16} style={{ color: "var(--accent-cyan)" }} /> Posting Guide</h3>
                  <div className="space-y-3 text-sm"><div><p className="text-xs" style={{ color: "var(--text-dim)" }}>Best Time</p><p className="font-medium">{content.best_posting_time}</p></div>
                    <div><p className="text-xs" style={{ color: "var(--text-dim)" }}>Format</p><p className="font-medium">{content.content_format}</p></div>
                    <div><p className="text-xs" style={{ color: "var(--text-dim)" }}>CTA</p><p style={{ color: "var(--text-muted)" }}>{content.cta}</p></div></div></div>
              </div>
            </div>}
            
            {virality && <div className="space-y-4">
              <div className="glass-card p-6 flex flex-col items-center animate-pulse-glow"><ScoreGauge score={virality.virality_score} grade={virality.grade} size={180} />
                <p className="text-sm mt-4" style={{ color: "var(--text-muted)" }}>Confidence: <span className="font-semibold">{(virality.confidence*100).toFixed(0)}%</span></p></div>
              <div className="glass-card p-5"><h3 className="font-semibold text-sm mb-3">Score Breakdown</h3>
                <div className="space-y-2.5">{virality.breakdown && Object.entries(virality.breakdown).map(([k, v]) => (
                  <div key={k}><div className="flex justify-between text-xs mb-1"><span style={{ color: "var(--text-muted)" }}>{k.split("_").map(w => w.charAt(0).toUpperCase()+w.slice(1)).join(" ")}</span><span className="font-semibold">{v as number}</span></div>
                    <div className="h-1.5 rounded-full" style={{ background: "var(--bg-secondary)" }}><div className="h-full rounded-full" style={{ width: `${v as number}%`, background: (v as number) >= 70 ? "#10b981" : (v as number) >= 50 ? "#f59e0b" : "#ef4444" }} /></div></div>))}</div></div>
              <div className="glass-card p-5"><h3 className="font-semibold text-sm mb-3">Predictions</h3>
                <div className="grid grid-cols-2 gap-3"><div className="p-3 rounded-xl" style={{ background: "var(--bg-secondary)" }}><p className="text-xs" style={{ color: "var(--text-dim)" }}>Reach</p><p className="text-lg font-bold" style={{ color: "var(--accent-light)" }}>{virality.predicted_reach >= 1000 ? `${(virality.predicted_reach/1000).toFixed(1)}K` : virality.predicted_reach}</p></div>
                  <div className="p-3 rounded-xl" style={{ background: "var(--bg-secondary)" }}><p className="text-xs" style={{ color: "var(--text-dim)" }}>Engagement</p><p className="text-lg font-bold" style={{ color: "var(--success)" }}>{virality.predicted_engagement_rate}%</p></div></div></div>
              <div className="glass-card p-5"><h3 className="font-semibold text-sm mb-3 flex items-center gap-2"><Lightbulb size={14} style={{ color: "var(--warning)" }} /> Improvements</h3>
                <ul className="space-y-2">{virality.improvements?.map((t, i) => <li key={i} className="flex items-start gap-2 text-xs" style={{ color: "var(--text-muted)" }}><span className="font-bold" style={{ color: "var(--accent-light)" }}>{i+1}.</span>{t}</li>)}</ul></div>
            </div>}
          </div>
        )}

        {!loading && !content && !virality && !error && (
          <div className="text-center py-16 animate-fade-in">
            <div className="w-20 h-20 rounded-2xl mx-auto mb-5 flex items-center justify-center animate-pulse-glow" style={{ background: "linear-gradient(135deg, rgba(6,182,212,0.15), rgba(124,58,237,0.1))", border: "1px solid rgba(6,182,212,0.2)" }}>
              <Sparkles size={36} style={{ color: "var(--accent-cyan)" }} /></div>
            <h3 className="text-xl font-semibold mb-2">AI Content Studio</h3>
            <p className="text-sm max-w-lg mx-auto" style={{ color: "var(--text-muted)" }}>Enter your topic and our AI agents will generate hooks, captions, hashtags, and predict viral potential — all in one click.</p>
          </div>
        )}
      </main>
    </div>
  );
}