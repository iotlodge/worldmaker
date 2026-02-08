"use client";

import { useState } from "react";
import { useGenerate, useGeneratePreview, useReset } from "@/hooks/use-generator";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Sparkles, RotateCcw, Eye, Play, AlertTriangle } from "lucide-react";

const SIZES = [
  { value: "small", label: "Small", desc: "~10 services" },
  { value: "medium", label: "Medium", desc: "~50 services" },
  { value: "large", label: "Large", desc: "~200 services" },
];

export default function GeneratorPage() {
  const [size, setSize] = useState("small");
  const [seed, setSeed] = useState<number>(42);
  const [withTraces, setWithTraces] = useState(true);
  const [confirmReset, setConfirmReset] = useState(false);

  const generate = useGenerate();
  const preview = useGeneratePreview();
  const reset = useReset();

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold">Ecosystem Generator</h1>
        <p className="text-sm text-muted-fg mt-1">
          Generate synthetic enterprise ecosystem data with realistic structure
        </p>
      </div>

      {/* Configuration */}
      <Card>
        <CardTitle>Configuration</CardTitle>
        <CardContent className="mt-4 space-y-5">
          {/* Size */}
          <div>
            <label className="text-sm font-medium mb-2 block">
              Ecosystem Size
            </label>
            <div className="grid grid-cols-3 gap-3">
              {SIZES.map((s) => (
                <button
                  key={s.value}
                  onClick={() => setSize(s.value)}
                  className={`rounded-lg border p-3 text-left transition-colors ${
                    size === s.value
                      ? "border-accent bg-accent/5"
                      : "border-card-border hover:border-accent/30"
                  }`}
                >
                  <p className="text-sm font-medium">{s.label}</p>
                  <p className="text-xs text-muted-fg mt-0.5">{s.desc}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Seed */}
          <div>
            <label className="text-sm font-medium mb-2 block">
              Random Seed
            </label>
            <input
              type="number"
              value={seed}
              onChange={(e) => setSeed(parseInt(e.target.value) || 0)}
              className="h-9 w-40 px-3 text-sm rounded-lg border border-card-border bg-card-bg text-foreground font-mono"
            />
            <p className="text-xs text-muted-fg mt-1">
              Same seed + size = identical output
            </p>
          </div>

          {/* Traces toggle */}
          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="traces"
              checked={withTraces}
              onChange={(e) => setWithTraces(e.target.checked)}
              className="rounded"
            />
            <label htmlFor="traces" className="text-sm">
              Generate traces for each flow
            </label>
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex gap-3">
        <Button
          variant="outline"
          onClick={() => preview.mutate({ size, seed })}
          disabled={preview.isPending}
        >
          <Eye className="w-4 h-4" />
          {preview.isPending ? "Loading..." : "Preview"}
        </Button>
        <Button
          onClick={() =>
            generate.mutate({ size, seed, with_traces: withTraces })
          }
          disabled={generate.isPending}
        >
          <Play className="w-4 h-4" />
          {generate.isPending ? "Generating..." : "Generate Ecosystem"}
        </Button>
      </div>

      {/* Preview result */}
      {preview.data && (
        <Card>
          <CardTitle>Preview</CardTitle>
          <CardContent className="mt-3">
            <p className="text-sm text-muted-fg mb-3">
              Seed: {preview.data.seed} • Size: {preview.data.size} •{" "}
              {preview.data.preview.total_entities} total entities
            </p>
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(preview.data.preview.breakdown).map(
                ([key, count]) => (
                  <div
                    key={key}
                    className="flex items-center justify-between text-sm py-1"
                  >
                    <span className="capitalize text-muted-fg">{key}</span>
                    <span className="font-mono font-medium">{count}</span>
                  </div>
                )
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Generation result */}
      {generate.data && (
        <Card className="border-emerald-200 dark:border-emerald-900/50">
          <CardTitle>
            <span className="flex items-center gap-2 text-emerald-500">
              <Sparkles className="w-4 h-4" />
              Generation Complete
            </span>
          </CardTitle>
          <CardContent className="mt-3 space-y-3">
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(generate.data.loaded).map(([key, count]) => (
                <div
                  key={key}
                  className="flex items-center justify-between text-sm py-1"
                >
                  <span className="capitalize text-muted-fg">{key}</span>
                  <span className="font-mono font-medium">{count}</span>
                </div>
              ))}
            </div>
            {generate.data.traces_generated !== undefined && (
              <p className="text-sm text-muted-fg">
                {generate.data.traces_generated} traces generated ({generate.data.total_spans} spans)
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Reset */}
      <Card className="border-red-200/50 dark:border-red-900/30">
        <CardTitle>
          <span className="flex items-center gap-2 text-red-500">
            <AlertTriangle className="w-4 h-4" />
            Danger Zone
          </span>
        </CardTitle>
        <CardContent className="mt-3">
          <p className="text-sm text-muted-fg mb-3">
            Reset clears all data from the in-memory store. This cannot be
            undone.
          </p>
          {!confirmReset ? (
            <Button
              variant="destructive"
              size="sm"
              onClick={() => setConfirmReset(true)}
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Reset Ecosystem
            </Button>
          ) : (
            <div className="flex items-center gap-3">
              <Button
                variant="destructive"
                size="sm"
                onClick={() => {
                  reset.mutate(undefined, {
                    onSuccess: () => {
                      generate.reset();
                      preview.reset();
                    },
                  });
                  setConfirmReset(false);
                }}
                disabled={reset.isPending}
              >
                {reset.isPending ? "Resetting..." : "Confirm Reset"}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setConfirmReset(false)}
              >
                Cancel
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
