"use client";

import { useEffect, useState } from "react";

const particles = Array.from({ length: 10 }, (_, index) => index);

export default function AppBootOverlay() {
  const [visible, setVisible] = useState(false);
  const [closing, setClosing] = useState(false);

  useEffect(() => {
    const hasSeenBoot = sessionStorage.getItem("viral-ai-boot-seen");

    if (hasSeenBoot) {
      return;
    }

    setVisible(true);
    sessionStorage.setItem("viral-ai-boot-seen", "true");

    // ⚡ Fast & snappy animation (UPDATED)
    const closeTimer = setTimeout(() => setClosing(true), 500);
    const hideTimer = setTimeout(() => setVisible(false), 1000);

    return () => {
      window.clearTimeout(closeTimer);
      window.clearTimeout(hideTimer);
    };
  }, []);

  if (!visible) {
    return null;
  }

  return (
    <div className={`boot-overlay ${closing ? "boot-overlay-hidden" : ""}`}>
      <div className="boot-grid" />

      <div className="boot-loader-shell">
        <div className="boot-loader-core">
          <div className="boot-ring boot-ring-outer" />
          <div className="boot-ring boot-ring-inner" />
          <div className="boot-pulse" />

          {particles.map((particle) => (
            <span
              key={particle}
              className="boot-particle"
              style={{ ["--particle-index"]: particle }}
            />
          ))}
        </div>

        <div className="boot-copy">
          <p className="boot-kicker">Loading workspace</p>
          <h2>Warming up your creator cockpit</h2>

          <div className="boot-progress">
            <span />
          </div>
        </div>
      </div>
    </div>
  );
}