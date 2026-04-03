"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  TrendingUp,
  Sparkles,
  Target,
  LogOut,
  Zap,
  Menu,
  X,
} from "lucide-react";
import { useState } from "react";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/trends", label: "Trend Discovery", icon: TrendingUp },
  { href: "/content-studio", label: "Content Studio", icon: Sparkles },
  { href: "/strategy", label: "Strategy", icon: Target },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    window.location.href = "/login";
  };

  return (
    <>
      {/* Mobile toggle */}
      <button
        onClick={() => setMobileOpen(!mobileOpen)}
        aria-label="Toggle navigation"
        className="fixed top-4 left-4 z-50 md:hidden rounded-2xl border p-2.5 shadow-lg backdrop-blur"
        style={{
          background: "rgba(9, 16, 28, 0.92)",
          borderColor: "rgba(255,255,255,0.08)",
        }}
      >
        {mobileOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/60 z-30 md:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 h-full z-40 flex flex-col transition-transform duration-300 ${
          mobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        }`}
        style={{
          width: 260,
          background:
            "linear-gradient(180deg, rgba(8, 15, 26, 0.98), rgba(7, 11, 20, 0.98))",
          borderRight: "1px solid rgba(255,255,255,0.08)",
          boxShadow: "0 0 45px rgba(0,0,0,0.22)",
        }}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-6 py-6 mb-2">
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center"
            style={{
              background: "linear-gradient(135deg, var(--accent), var(--accent-cyan))",
              boxShadow: "0 14px 30px rgba(15, 118, 110, 0.2)",
            }}
          >
            <Zap size={20} color="white" />
          </div>
          <div>
            <h1 className="text-base font-bold tracking-tight">Viral AI</h1>
            <p className="text-xs" style={{ color: "var(--text-dim)" }}>
              Content Intelligence
            </p>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3">
          <p
            className="text-[11px] font-semibold uppercase tracking-widest px-3 mb-3"
            style={{ color: "var(--text-dim)" }}
          >
            Main Menu
          </p>
          <ul className="space-y-1">
            {navItems.map((item) => {
              const isActive =
                pathname === item.href ||
                (item.href !== "/" && pathname.startsWith(item.href));
              const Icon = item.icon;
              return (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    onClick={() => setMobileOpen(false)}
                    className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                      isActive ? "" : "hover:bg-white/5"
                    }`}
                    style={{
                      color: isActive ? "white" : "var(--text-muted)",
                      background: isActive
                        ? "linear-gradient(135deg, rgba(124,58,237,0.2), rgba(6,182,212,0.1))"
                        : undefined,
                      border: isActive ? "1px solid rgba(124,58,237,0.3)" : "1px solid transparent",
                    }}
                  >
                    <Icon size={18} style={{ color: isActive ? "var(--accent-light)" : undefined }} />
                    {item.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Footer */}
        <div className="px-3 pb-6">
          <div
            className="rounded-xl p-4 mb-3"
            style={{
              background:
                "linear-gradient(135deg, rgba(245,158,11,0.12), rgba(15,118,110,0.08))",
              border: "1px solid rgba(245,158,11,0.18)",
            }}
          >
            <p className="text-xs font-semibold mb-1" style={{ color: "var(--warning)" }}>
              Live Demo Workspace
            </p>
            <p className="text-[11px]" style={{ color: "var(--text-dim)" }}>
              Fallback data keeps the product usable even when AI providers are offline.
            </p>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-3 py-2 text-sm rounded-xl w-full hover:bg-white/5 transition-colors"
            style={{ color: "var(--text-dim)" }}
          >
            <LogOut size={16} />
            Logout
          </button>
        </div>
      </aside>
    </>
  );
}
