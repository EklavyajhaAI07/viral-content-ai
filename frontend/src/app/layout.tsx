import type { Metadata } from "next";
import localFont from "next/font/local";
import AppBootOverlay from "@/components/AppBootOverlay";
import SessionGate from "@/components/SessionGate";
import "./globals.css";

const appSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-sans",
  weight: "100 900",
  display: "swap",
});

const appMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-mono",
  weight: "100 900",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Viral AI — Content Intelligence Platform",
  description:
    "AI-powered viral content prediction, trend analysis, and optimization platform for creators and businesses.",
  keywords: "viral content, AI, social media, trend analysis, content optimization",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${appSans.variable} ${appMono.variable}`}>
        <AppBootOverlay />
        {/* Grid background */}
        <div className="grid-bg" />
        {/* Glow orbs */}
        <div
          className="glow-orb"
          style={{ top: "-100px", right: "-100px", background: "#f59e0b" }}
        />
        <div
          className="glow-orb"
          style={{ bottom: "-100px", left: "30%", background: "#0f766e" }}
        />
        <SessionGate>{children}</SessionGate>
      </body>
    </html>
  );
}
