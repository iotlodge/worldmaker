"use client";

import { usePathname } from "next/navigation";
import { Activity, ChevronRight } from "lucide-react";
import Link from "next/link";
import { ThemeToggle } from "@/components/theme-toggle";

/** Map pathname to breadcrumb segments */
function getBreadcrumbs(pathname: string): { label: string; href: string }[] {
  if (pathname === "/") return [{ label: "Dashboard", href: "/" }];

  const segments = pathname.split("/").filter(Boolean);
  const crumbs: { label: string; href: string }[] = [];
  let href = "";

  for (const seg of segments) {
    href += `/${seg}`;
    const label = seg
      .split("-")
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join(" ");
    crumbs.push({ label, href });
  }

  return crumbs;
}

export function Header() {
  const pathname = usePathname();
  const breadcrumbs = getBreadcrumbs(pathname);

  return (
    <header className="flex items-center justify-between h-14 px-6 border-b border-card-border bg-card-bg/80 backdrop-blur-sm">
      {/* Breadcrumbs */}
      <nav className="flex items-center gap-1.5 text-sm">
        {breadcrumbs.map((crumb, i) => (
          <span key={crumb.href} className="flex items-center gap-1.5">
            {i > 0 && (
              <ChevronRight className="w-3.5 h-3.5 text-muted-fg" />
            )}
            {i === breadcrumbs.length - 1 ? (
              <span className="font-medium text-foreground">
                {crumb.label}
              </span>
            ) : (
              <Link
                href={crumb.href}
                className="text-muted-fg hover:text-foreground transition-colors"
              >
                {crumb.label}
              </Link>
            )}
          </span>
        ))}
      </nav>

      {/* Right side — theme toggle + status */}
      <div className="flex items-center gap-4">
        <ThemeToggle />
        <div className="flex items-center gap-2 text-xs text-muted-fg">
          <Activity className="w-3.5 h-3.5" />
          <span>API</span>
          <span className="inline-block w-2 h-2 rounded-full bg-emerald-500" />
        </div>
      </div>
    </header>
  );
}
