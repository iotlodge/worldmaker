"use client";

import { useState } from "react";
import { useEcosystemSearch } from "@/hooks/use-ecosystem";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/loading";
import { formatEntityType, shortId } from "@/lib/utils";
import { Search as SearchIcon } from "lucide-react";
import Link from "next/link";

const ENTITY_LINKS: Record<string, string> = {
  product: "/products",
  platform: "/platforms",
  service: "/services",
  flow: "/flows",
};

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const { data, isLoading } = useEcosystemSearch(query);

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold">Search</h1>
        <p className="text-sm text-muted-fg mt-1">
          Search across all entities in the ecosystem
        </p>
      </div>

      <div className="relative">
        <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-fg" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by name, ID, or keyword..."
          className="w-full h-10 pl-10 pr-4 text-sm rounded-lg border border-card-border bg-card-bg text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          autoFocus
        />
      </div>

      {query.length === 0 ? (
        <EmptyState
          icon={SearchIcon}
          title="Start typing to search"
          description="Search across products, platforms, services, flows, and more"
        />
      ) : isLoading ? (
        <p className="text-sm text-muted-fg py-8 text-center">Searching...</p>
      ) : data && data.results.length > 0 ? (
        <div className="space-y-2">
          <p className="text-xs text-muted-fg">
            {data.total} result{data.total !== 1 ? "s" : ""} for "{data.query}"
          </p>
          {data.results.map((r, i) => {
            const base = ENTITY_LINKS[r.entity_type];
            const href = base ? `${base}/${r.entity.id}` : "#";
            return (
              <Link key={`${r.entity_type}-${r.entity.id}`} href={href}>
                <Card className="hover:border-accent/30 transition-colors cursor-pointer py-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-medium">
                        {r.entity.name ?? shortId(r.entity.id)}
                      </h3>
                      <Badge variant="outline" className="mt-1 text-xs">
                        {formatEntityType(r.entity_type)}
                      </Badge>
                    </div>
                    <span className="text-xs font-mono text-muted-fg">
                      {shortId(r.entity.id)}
                    </span>
                  </div>
                </Card>
              </Link>
            );
          })}
        </div>
      ) : (
        <EmptyState
          icon={SearchIcon}
          title="No results"
          description={`Nothing found for "${query}"`}
        />
      )}
    </div>
  );
}
