"use client";
import Sidebar from "@/components/Sidebar";
import { generateDemoStrategy } from "@/lib/demoData";
import { getApiErrorMessage, strategyAPI } from "@/lib/api";
import { StrategyData } from "@/types";
import { Target, Loader2, AlertCircle, Calendar, ArrowRightLeft, Rocket, Lightbulb, FlaskConical, TrendingUp } from "lucide-react";
import { useState } from "react";

const platforms = ["instagram","tiktok","youtube","linkedin","twitter"];

export default function StrategyPage() {
  const [topic, setTopic] = useState("");
  const [platform, setPlatform] = useState("instagram");
  const [strategy, setStrategy] = useState<StrategyData|null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [source, setSource] = useState("idle");

  const handleGenerate = async () => {
    if(!topic.trim()) return;
    setLoading(true); setError(""); setStrategy(null); setSource("idle");
    try {
      const res = await strategyAPI.generate({ topic: topic.trim(), platform });
      setStrategy(res.data as unknown as StrategyData);
      setSource(res.source || "api");
    } catch (e: unknown) {
      setStrategy(generateDemoStrategy(topic.trim(), platform));
      setSource("offline_demo");
      setError(`Backend unavailable, so a local demo strategy is shown instead. ${getApiErrorMessage(e, "")}`.trim());
    }
    finally { setLoading(false); }
  };

  const priorityColor = (p:string) => p==="high" ? "#ef4444" : "#f59e0b";

  return (
    <div className="app-shell"><Sidebar/>
      <main className="page-content">
        <div className="page-hero animate-fade-in">
          <div className="hero-kicker">Planning engine</div>
          <h1 className="text-2xl md:text-4xl font-bold flex items-center gap-3"><Target size={28} style={{color:"var(--accent-light)"}}/> Strategy Generator</h1>
          <p className="mt-3 max-w-2xl" style={{color:"var(--text-muted)"}}>Turn one topic into a weekly calendar, repurposing flow, testing plan, and 30-day growth forecast.</p>
          <div className="status-strip mt-5">
            <div className="status-chip">7-day publishing map</div>
            <div className="status-chip">Repurposing workflow for 5 channels</div>
            <div className="status-chip">Forecast and experimentation plan</div>
          </div>
        </div>

        <div className="glass-card p-6 mb-6 animate-fade-in-up">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-1"><label className="text-sm font-medium mb-2 block" style={{color:"var(--text-muted)"}}>Topic *</label>
              <input className="input-field" placeholder="e.g., Personal branding for developers" value={topic} onChange={e=>setTopic(e.target.value)} onKeyDown={e=>e.key==="Enter"&&handleGenerate()}/></div>
            <div><label className="text-sm font-medium mb-2 block" style={{color:"var(--text-muted)"}}>Primary Platform</label>
              <select className="input-field" value={platform} onChange={e=>setPlatform(e.target.value)}>{platforms.map(p=><option key={p} value={p}>{p[0].toUpperCase()+p.slice(1)}</option>)}</select></div>
            <div className="flex items-end"><button className="btn-primary w-full" onClick={handleGenerate} disabled={loading||!topic.trim()}>
              {loading?<><Loader2 size={16} className="animate-spin"/> Generating...</>:<><Rocket size={16}/> Generate Strategy</>}</button></div>
          </div>
        </div>

        {error&&<div className="flex items-center gap-3 p-4 rounded-xl mb-6" style={{background:"rgba(239,68,68,0.1)",border:"1px solid rgba(239,68,68,0.3)"}}><AlertCircle size={18} style={{color:"#ef4444"}}/><p className="text-sm" style={{color:"#ef4444"}}>{error}</p></div>}

        {source !== "idle" && (
          <div className="source-banner mb-6">
            <span className="badge badge-platform">
              {source === "offline_demo" ? "Offline demo" : source}
            </span>
            <p>
              {source === "offline_demo"
                ? "Strategy generation is still available with seeded local planning data."
                : "Strategy output came from the backend flow."}
            </p>
          </div>
        )}

        {loading&&<div className="space-y-4">{[1,2,3].map(i=><div key={i} className="glass-card p-6"><div className="skeleton h-6 w-48 mb-4"/><div className="skeleton h-4 w-full mb-2"/><div className="skeleton h-4 w-3/4"/></div>)}</div>}

        {!loading&&strategy&&(
          <div className="space-y-6 animate-fade-in-up">
            {/* 7-Day Calendar */}
            <div className="glass-card p-6">
              <h2 className="text-lg font-semibold flex items-center gap-2 mb-4"><Calendar size={20} style={{color:"var(--accent-light)"}}/> 7-Day Content Calendar</h2>
              <div className="table-scroll">
                <table className="w-full text-sm">
                  <thead><tr style={{borderBottom:"1px solid var(--border)"}}>
                    {["Day","Platform","Type","Topic","Time","Priority"].map(h=><th key={h} className="text-left py-3 px-4 font-semibold" style={{color:"var(--text-dim)"}}>{h}</th>)}</tr></thead>
                  <tbody>{strategy.calendar?.map((day,i)=>(
                    <tr key={i} className="hover:bg-white/5 transition-colors" style={{borderBottom:"1px solid var(--border)"}}>
                      <td className="py-3 px-4 font-medium">{day.day}<br/><span className="text-[11px]" style={{color:"var(--text-dim)"}}>{day.date}</span></td>
                      <td className="py-3 px-4"><span className={`badge badge-platform text-[11px]`}>{day.platform}</span></td>
                      <td className="py-3 px-4" style={{color:"var(--text-muted)"}}>{day.content_type}</td>
                      <td className="py-3 px-4 max-w-[250px]" style={{color:"var(--text-muted)"}}>{day.topic_angle}</td>
                      <td className="py-3 px-4" style={{color:"var(--accent-cyan)"}}>{day.post_time}</td>
                      <td className="py-3 px-4"><span className="text-xs font-bold uppercase" style={{color:priorityColor(day.priority)}}>{day.priority}</span></td>
                    </tr>))}</tbody>
                </table>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Repurposing Plan */}
              <div className="glass-card p-6">
                <h2 className="text-lg font-semibold flex items-center gap-2 mb-4"><ArrowRightLeft size={20} style={{color:"var(--accent-cyan)"}}/> Repurposing Plan</h2>
                <div className="space-y-3">{strategy.repurposing_plan&&Object.entries(strategy.repurposing_plan).map(([k,v])=>(
                  <div key={k} className="flex items-start gap-3 p-3 rounded-xl" style={{background:"var(--bg-secondary)"}}>
                    <span className="badge badge-platform text-[10px] mt-0.5 flex-shrink-0">{k}</span>
                    <p className="text-sm" style={{color:"var(--text-muted)"}}>{v}</p>
                  </div>))}</div>
              </div>

              {/* Growth Strategy */}
              <div className="glass-card p-6">
                <h2 className="text-lg font-semibold flex items-center gap-2 mb-4"><Rocket size={20} style={{color:"var(--success)"}}/> Growth Strategy</h2>
                <div className="space-y-4">{strategy.growth_strategy&&Object.entries(strategy.growth_strategy).map(([k,v])=>(
                  <div key={k}>
                    <h4 className="font-semibold text-sm mb-2" style={{color:"var(--accent-light)"}}>{v.title}</h4>
                    <ul className="space-y-1.5">{v.actions.map((a,i)=><li key={i} className="flex items-start gap-2 text-xs" style={{color:"var(--text-muted)"}}>
                      <span style={{color:"var(--success)"}}>•</span>{a}</li>)}</ul>
                  </div>))}</div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Content Gaps */}
              <div className="glass-card p-6">
                <h2 className="font-semibold flex items-center gap-2 mb-4"><Lightbulb size={18} style={{color:"var(--warning)"}}/> Content Gaps</h2>
                <div className="space-y-3">{strategy.content_gaps?.map((g,i)=>(
                  <div key={i} className="p-3 rounded-xl" style={{background:"var(--bg-secondary)"}}>
                    <p className="text-sm font-medium mb-1">{g.gap}</p>
                    <p className="text-xs" style={{color:"var(--text-dim)"}}>{g.opportunity}</p>
                    <p className="text-xs font-bold mt-1" style={{color:"var(--success)"}}>Viral potential: {g.viral_potential}</p>
                  </div>))}</div>
              </div>

              {/* A/B Tests */}
              <div className="glass-card p-6">
                <h2 className="font-semibold flex items-center gap-2 mb-4"><FlaskConical size={18} style={{color:"var(--accent-cyan)"}}/> A/B Tests</h2>
                <div className="space-y-3">{strategy.ab_tests?.map((t,i)=>(
                  <div key={i} className="p-3 rounded-xl" style={{background:"var(--bg-secondary)"}}>
                    <p className="text-sm font-medium mb-2">{t.element}</p>
                    <div className="grid grid-cols-2 gap-2 text-xs"><div><span style={{color:"var(--text-dim)"}}>A:</span> <span style={{color:"var(--text-muted)"}}>{t.variant_a}</span></div>
                      <div><span style={{color:"var(--text-dim)"}}>B:</span> <span style={{color:"var(--text-muted)"}}>{t.variant_b}</span></div></div>
                    <p className="text-[11px] mt-1" style={{color:"var(--accent-light)"}}>Metric: {t.metric}</p>
                  </div>))}</div>
              </div>

              {/* 30-Day Forecast */}
              <div className="glass-card p-6">
                <h2 className="font-semibold flex items-center gap-2 mb-4"><TrendingUp size={18} style={{color:"var(--accent-light)"}}/> 30-Day Forecast</h2>
                {strategy.forecast_30_day&&<div className="space-y-3">{Object.entries(strategy.forecast_30_day).map(([k,v])=>(
                  <div key={k} className="flex justify-between items-center p-3 rounded-xl" style={{background:"var(--bg-secondary)"}}>
                    <span className="text-xs capitalize" style={{color:"var(--text-dim)"}}>{k.replace(/_/g," ")}</span>
                    <span className="text-sm font-bold" style={{color:"var(--accent-light)"}}>{v}</span>
                  </div>))}</div>}
              </div>
            </div>
          </div>
        )}

        {!loading&&!strategy&&!error&&(
          <div className="text-center py-16 animate-fade-in">
            <div className="w-20 h-20 rounded-2xl mx-auto mb-5 flex items-center justify-center animate-pulse-glow" style={{background:"linear-gradient(135deg, rgba(16,185,129,0.15), rgba(124,58,237,0.1))",border:"1px solid rgba(16,185,129,0.2)"}}>
              <Target size={36} style={{color:"var(--success)"}}/></div>
            <h3 className="text-xl font-semibold mb-2">AI Strategy Generator</h3>
            <p className="text-sm max-w-lg mx-auto" style={{color:"var(--text-muted)"}}>Enter a topic and get a complete 7-day content calendar, cross-platform repurposing plan, growth strategy, and 30-day forecast.</p>
          </div>
        )}
      </main>
    </div>
  );
}
