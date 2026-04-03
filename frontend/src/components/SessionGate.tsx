"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

const PUBLIC_PATHS = new Set(["/login"]);

export default function SessionGate({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    const token = localStorage.getItem("token");
    const hasSession = Boolean(storedUser || token);
    const isPublicPath = PUBLIC_PATHS.has(pathname);

    if (!hasSession && !isPublicPath) {
      router.replace("/login");
      return;
    }

    if (hasSession && pathname === "/login") {
      router.replace("/");
      return;
    }

    setReady(true);
  }, [pathname, router]);

  if (!ready) {
    return (
      <div className="route-loader">
        <div className="boot-loader-core route-loader-core">
          <div className="boot-ring boot-ring-outer" />
          <div className="boot-ring boot-ring-inner" />
          <div className="boot-pulse" />
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
