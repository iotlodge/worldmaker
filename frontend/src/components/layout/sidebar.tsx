"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Server,
  Container,
  GitBranch,
  Workflow,
  Activity,
  Package,
  Layers,
  Sparkles,
  Search,
  ShieldAlert,
  AlertOctagon,
  BookOpen,
  Building2,
  Tags,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

interface NavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  description?: string;
}

const NAV_SECTIONS: { title: string; items: NavItem[] }[] = [
  {
    title: "Overview",
    items: [
      {
        label: "Dashboard",
        href: "/",
        icon: LayoutDashboard,
        description: "Ecosystem overview",
      },
    ],
  },
  {
    title: "Enterprise",
    items: [
      {
        label: "Business View",
        href: "/enterprise",
        icon: Building2,
        description: "Core management platforms",
      },
    ],
  },
  {
    title: "Entities",
    items: [
      {
        label: "Products",
        href: "/products",
        icon: Package,
        description: "Product management",
      },
      {
        label: "Platforms",
        href: "/platforms",
        icon: Layers,
        description: "Platform & capabilities",
      },
      {
        label: "Services",
        href: "/services",
        icon: Server,
        description: "Service registry",
      },
      {
        label: "Microservices",
        href: "/microservices",
        icon: Container,
        description: "Deployment units",
      },
    ],
  },
  {
    title: "Analysis",
    items: [
      {
        label: "Risk Surface",
        href: "/risk-surface",
        icon: ShieldAlert,
        description: "Features & capabilities",
      },
      {
        label: "Issue Discovery",
        href: "/issues",
        icon: AlertOctagon,
        description: "Findings & circular deps",
      },
      {
        label: "Dependencies",
        href: "/dependencies",
        icon: GitBranch,
        description: "Dependency graph",
      },
      {
        label: "Flows",
        href: "/flows",
        icon: Workflow,
        description: "Flow management",
      },
      {
        label: "Observability",
        href: "/observability",
        icon: Activity,
        description: "Traces & spans",
      },
      {
        label: "Attributes",
        href: "/attributes",
        icon: Tags,
        description: "Attribute registry & gaps",
      },
    ],
  },
  {
    title: "Tools",
    items: [
      {
        label: "Generator",
        href: "/generator",
        icon: Sparkles,
        description: "Generate ecosystems",
      },
      {
        label: "API Reference",
        href: "/api-reference",
        icon: BookOpen,
        description: "Endpoint documentation",
      },
    ],
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  };

  return (
    <aside
      className={cn(
        "flex flex-col h-screen bg-sidebar-bg text-sidebar-fg border-r border-sidebar-border transition-all duration-200",
        collapsed ? "w-16" : "w-60"
      )}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 h-14 border-b border-sidebar-border">
        <div className="w-8 h-8 rounded-lg bg-sidebar-accent flex items-center justify-center text-white font-bold text-sm shrink-0">
          W
        </div>
        {!collapsed && (
          <span className="font-semibold text-sm tracking-tight whitespace-nowrap">
            WorldMaker
          </span>
        )}
      </div>

      {/* Search (expanded only) */}
      {!collapsed && (
        <div className="px-3 py-3">
          <Link
            href="/search"
            className="flex items-center gap-2 px-3 py-2 text-xs text-sidebar-muted rounded-md bg-sidebar-fg/5 hover:bg-sidebar-fg/10 transition-colors"
          >
            <Search className="w-3.5 h-3.5" />
            <span>Search ecosystem...</span>
          </Link>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-2 py-2 space-y-4">
        {NAV_SECTIONS.map((section) => (
          <div key={section.title}>
            {!collapsed && (
              <h3 className="px-3 mb-1 text-[10px] uppercase tracking-wider font-medium text-sidebar-muted/60">
                {section.title}
              </h3>
            )}
            <ul className="space-y-0.5">
              {section.items.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.href);
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      className={cn(
                        "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
                        active
                          ? "bg-sidebar-accent/15 text-sidebar-accent font-medium"
                          : "text-sidebar-fg/70 hover:bg-sidebar-fg/5 hover:text-sidebar-fg"
                      )}
                      title={collapsed ? item.label : undefined}
                    >
                      <Icon
                        className={cn(
                          "w-4 h-4 shrink-0",
                          active ? "text-sidebar-accent" : "text-sidebar-muted"
                        )}
                      />
                      {!collapsed && <span>{item.label}</span>}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="flex items-center justify-center h-10 border-t border-sidebar-border text-sidebar-muted hover:text-sidebar-fg transition-colors"
        title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
      >
        {collapsed ? (
          <ChevronRight className="w-4 h-4" />
        ) : (
          <ChevronLeft className="w-4 h-4" />
        )}
      </button>
    </aside>
  );
}
