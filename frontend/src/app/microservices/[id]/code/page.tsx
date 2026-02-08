"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import { useCodeManifest, useCodeFile } from "@/hooks/use-codegen";
import { useMicroservice } from "@/hooks/use-microservices";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageLoader, ErrorState, EmptyState } from "@/components/ui/loading";
import {
  FileCode,
  FolderOpen,
  ArrowLeft,
  FileText,
  Container as ContainerIcon,
  Copy,
  Check,
} from "lucide-react";
import Link from "next/link";

const LANG_COLORS: Record<string, string> = {
  python: "bg-blue-100 text-blue-800",
  go: "bg-cyan-100 text-cyan-800",
  typescript: "bg-blue-100 text-blue-800",
  java: "bg-orange-100 text-orange-800",
  rust: "bg-red-100 text-red-800",
  csharp: "bg-purple-100 text-purple-800",
};

const FILE_ICONS: Record<string, typeof FileCode> = {
  Dockerfile: ContainerIcon,
  README: FileText,
};

function getFileIcon(name: string) {
  for (const [key, Icon] of Object.entries(FILE_ICONS)) {
    if (name.includes(key)) return Icon;
  }
  return FileCode;
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  return `${(bytes / 1024).toFixed(1)} KB`;
}

export default function CodeViewerPage() {
  const params = useParams();
  const msId = params.id as string;
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const ms = useMicroservice(msId);
  const manifest = useCodeManifest(msId);
  const file = useCodeFile(msId, selectedFile ?? "");

  if (ms.isLoading || manifest.isLoading) return <PageLoader />;
  if (ms.isError) return <ErrorState message="Microservice not found" onRetry={() => ms.refetch()} />;
  if (manifest.isError)
    return (
      <EmptyState
        icon={FolderOpen}
        title="No code repository"
        description="Code hasn't been scaffolded for this microservice yet."
        action={
          <Link href="/microservices" className="text-sm text-accent hover:underline">
            ← Back to Microservices
          </Link>
        }
      />
    );

  const msData = ms.data;
  const files = manifest.data?.files ?? [];
  const language = manifest.data?.language ?? "unknown";

  const handleCopy = async () => {
    if (file.data?.content) {
      await navigator.clipboard.writeText(file.data.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link
          href="/microservices"
          className="w-8 h-8 rounded-lg border border-card-border flex items-center justify-center hover:border-accent/40 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
        </Link>
        <div className="flex-1">
          <h1 className="text-2xl font-bold">{msData?.name ?? "Code Repository"}</h1>
          <div className="flex items-center gap-2 mt-1">
            <Badge className={LANG_COLORS[language] ?? "bg-gray-100 text-gray-800"}>
              {language}
            </Badge>
            {manifest.data?.framework && (
              <span className="text-xs text-muted-fg">{manifest.data.framework}</span>
            )}
            <span className="text-xs text-muted-fg">
              {files.length} file{files.length !== 1 ? "s" : ""}
            </span>
          </div>
        </div>
      </div>

      {/* Two-panel layout: file list + viewer */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* File list */}
        <Card className="lg:col-span-1">
          <CardTitle className="flex items-center gap-2">
            <FolderOpen className="w-4 h-4" />
            Files
          </CardTitle>
          <CardContent className="mt-3 space-y-1">
            {files.map((f) => {
              const Icon = getFileIcon(f.name);
              const isSelected = selectedFile === f.name;
              return (
                <button
                  key={f.name}
                  onClick={() => setSelectedFile(f.name)}
                  className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left text-sm transition-colors ${
                    isSelected
                      ? "bg-accent/10 text-accent border border-accent/20"
                      : "hover:bg-card-bg-hover"
                  }`}
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  <span className="truncate font-mono text-xs">{f.name}</span>
                  <span className="ml-auto text-xs text-muted-fg shrink-0">
                    {formatBytes(f.size)}
                  </span>
                </button>
              );
            })}
          </CardContent>
        </Card>

        {/* Code viewer */}
        <Card className="lg:col-span-3">
          {!selectedFile ? (
            <div className="flex flex-col items-center justify-center py-16 text-muted-fg">
              <FileCode className="w-10 h-10 mb-3 opacity-40" />
              <p className="text-sm">Select a file to view its contents</p>
            </div>
          ) : file.isLoading ? (
            <div className="flex items-center justify-center py-16">
              <div className="animate-spin rounded-full h-6 w-6 border-2 border-accent border-t-transparent" />
            </div>
          ) : file.isError ? (
            <div className="py-8 text-center text-sm text-red-500">
              Failed to load file content
            </div>
          ) : (
            <>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2 font-mono text-sm">
                  <FileCode className="w-4 h-4" />
                  {selectedFile}
                </CardTitle>
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-1.5 text-xs text-muted-fg hover:text-foreground transition-colors"
                >
                  {copied ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-500" />
                      <span className="text-emerald-500">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      <span>Copy</span>
                    </>
                  )}
                </button>
              </div>
              <CardContent className="mt-3">
                <pre className="bg-[var(--bg)] rounded-lg p-4 overflow-x-auto text-xs leading-relaxed font-mono border border-card-border">
                  <code>{file.data?.content ?? ""}</code>
                </pre>
              </CardContent>
            </>
          )}
        </Card>
      </div>
    </div>
  );
}
