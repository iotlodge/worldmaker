"use client";

import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import { Sun, Moon, Monitor } from "lucide-react";
import { cn } from "@/lib/utils";

const MODES = [
  { value: "light", icon: Sun, label: "Light" },
  { value: "system", icon: Monitor, label: "System" },
  { value: "dark", icon: Moon, label: "Dark" },
] as const;

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Avoid hydration mismatch — render after mount
  useEffect(() => setMounted(true), []);

  if (!mounted) {
    return <div className="h-7 w-[84px] rounded-full bg-muted/30" />;
  }

  return (
    <div className="flex items-center h-7 rounded-full bg-muted/40 border border-card-border p-0.5 gap-0.5">
      {MODES.map(({ value, icon: Icon, label }) => (
        <button
          key={value}
          onClick={() => setTheme(value)}
          className={cn(
            "flex items-center justify-center w-6 h-6 rounded-full transition-all",
            theme === value
              ? "bg-accent text-accent-fg shadow-sm"
              : "text-muted-fg hover:text-foreground"
          )}
          title={label}
          aria-label={`Switch to ${label} mode`}
        >
          <Icon className="w-3 h-3" />
        </button>
      ))}
    </div>
  );
}
