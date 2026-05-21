"use client";

import { useEffect, useMemo, useState } from "react";
import { Database, FlaskConical, Plus, RefreshCw } from "lucide-react";

import { DiffHighlight } from "@/components/diff-highlight";
import { DriftChart } from "@/components/drift-chart";
import { EmbeddingCluster } from "@/components/embedding-cluster";
import { ConsistencyRadarChart } from "@/components/radar-chart";
import { RiskSummary } from "@/components/risk-summary";
import { Timeline } from "@/components/timeline";
import { UploadDropzone } from "@/components/upload-dropzone";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import type { AnalysisResult, ClusterPoint, Delegate, DelegateProfile } from "@/lib/types";
import { cn } from "@/lib/utils";

export function DashboardShell({ initialDelegateId }: { initialDelegateId?: string }) {
  const [delegates, setDelegates] = useState<Delegate[]>([]);
  const [selectedId, setSelectedId] = useState<string | undefined>(initialDelegateId);
  const [profile, setProfile] = useState<DelegateProfile | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [newDelegateName, setNewDelegateName] = useState("");

  async function refreshDelegates(preferredId?: string) {
    setLoading(true);
    try {
      let rows = await api.listDelegates();
      if (rows.length === 0) {
        await api.seedDemo();
        rows = await api.listDelegates();
      }
      setDelegates(rows);
      const nextId = preferredId ?? selectedId ?? rows[0]?.id;
      setSelectedId(nextId);
      if (nextId) {
        setProfile(await api.getProfile(nextId));
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to load workspace.");
    } finally {
      setLoading(false);
    }
  }

  async function createDelegate() {
    if (!newDelegateName.trim()) return;
    const delegate = await api.createDelegate({ name: newDelegateName.trim(), country: "Unassigned", committee: "General Assembly" });
    setNewDelegateName("");
    await refreshDelegates(delegate.id);
  }

  useEffect(() => {
    void refreshDelegates(initialDelegateId);
    // 初次加载即可，后续切换通过显式 handler 控制。
  }, [initialDelegateId]);

  async function switchDelegate(delegateId: string) {
    setSelectedId(delegateId);
    setAnalysis(null);
    setProfile(await api.getProfile(delegateId));
  }

  const clusterPoints = useMemo<ClusterPoint[]>(() => {
    const base = profile?.embedding_stats?.cluster_points ?? [];
    if (!analysis) return base;
    return [...base, { label: "Current analysis", x: analysis.semanticDrift, y: analysis.stylometricShift, kind: "analysis" }];
  }, [analysis, profile]);

  return (
    <main className="min-h-screen bg-background">
      <div className="mx-auto flex max-w-[1500px] gap-6 px-6 py-6">
        <aside className="sticky top-6 hidden h-[calc(100vh-48px)] w-80 shrink-0 flex-col rounded-lg border border-border bg-panel p-4 lg:flex">
          <div className="mb-6 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent text-slate-950">
              <FlaskConical className="h-5 w-5" />
            </div>
            <div>
              <div className="text-sm font-semibold">Writing Consistency</div>
              <div className="text-xs text-muted">Research platform</div>
            </div>
          </div>

          <div className="space-y-2">
            <div className="text-xs uppercase tracking-[0.14em] text-muted">Delegates</div>
            {delegates.map((delegate) => (
              <button
                key={delegate.id}
                className={cn("w-full rounded-md border border-transparent px-3 py-3 text-left text-sm transition-colors hover:bg-panelSoft", selectedId === delegate.id && "border-border bg-panelSoft")}
                onClick={() => void switchDelegate(delegate.id)}
              >
                <div className="font-medium">{delegate.name}</div>
                <div className="text-xs text-muted">{delegate.committee ?? "No committee"} · {delegate.document_count} docs</div>
              </button>
            ))}
          </div>

          <div className="mt-auto space-y-2">
            <input className="w-full rounded-md border border-border bg-panelSoft px-3 py-2 text-sm outline-none focus:border-accent" value={newDelegateName} onChange={(event) => setNewDelegateName(event.target.value)} placeholder="New delegate name" />
            <Button className="w-full" variant="secondary" onClick={() => void createDelegate()}>
              <Plus className="mr-2 h-4 w-4" />
              Create Profile
            </Button>
          </div>
        </aside>

        <section className="min-w-0 flex-1">
          <header className="mb-6 flex flex-col gap-4 border-b border-border pb-5 md:flex-row md:items-end md:justify-between">
            <div>
              <div className="mb-2 flex items-center gap-2">
                <Badge>Consistency Analysis</Badge>
                <Badge>Stylometry</Badge>
                <Badge>Embedding Baseline</Badge>
              </div>
              <h1 className="text-3xl font-semibold tracking-normal">Delegate Writing Consistency Analyzer</h1>
              <p className="mt-2 max-w-3xl text-sm text-muted">Compare a new document against a delegate&apos;s historical writing profile through stylometric shift, semantic drift, and revision anomaly indicators.</p>
            </div>
            <Button variant="secondary" onClick={() => void refreshDelegates()}>
              <RefreshCw className="mr-2 h-4 w-4" />
              Refresh
            </Button>
          </header>

          {message ? <div className="mb-4 rounded-md border border-warning/40 bg-warning/10 p-3 text-sm text-warning">{message}</div> : null}
          {loading ? <div className="rounded-lg border border-border bg-panel p-8 text-sm text-muted">Loading workspace...</div> : null}

          {!loading && profile ? (
            <div className="grid gap-5">
              <div className="grid grid-cols-1 gap-5 xl:grid-cols-[1.1fr_0.9fr]">
                <Card>
                  <CardHeader>
                    <CardTitle>Delegate Profile</CardTitle>
                    <Badge>{profile.delegate.document_count} history documents</Badge>
                  </CardHeader>
                  <div className="grid gap-4 md:grid-cols-4">
                    <ProfileMetric label="Name" value={profile.delegate.name} />
                    <ProfileMetric label="Country" value={profile.delegate.country ?? "—"} />
                    <ProfileMetric label="Committee" value={profile.delegate.committee ?? "—"} />
                    <ProfileMetric label="Baseline" value={profile.embedding_stats ? "Ready" : "Pending"} />
                  </div>
                </Card>
                <RiskSummary result={analysis} />
              </div>

              <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle>Upload Historical Writing</CardTitle>
                    <Database className="h-4 w-4 text-muted" />
                  </CardHeader>
                  <UploadDropzone delegateId={selectedId} mode="history" onUploaded={() => void refreshDelegates(selectedId)} />
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle>Analyze New Document</CardTitle>
                    <FlaskConical className="h-4 w-4 text-muted" />
                  </CardHeader>
                  <UploadDropzone delegateId={selectedId} mode="analysis" onAnalyzed={(response) => setAnalysis(response.result)} />
                </Card>
              </div>

              <div className="grid grid-cols-1 gap-5 xl:grid-cols-3">
                <Timeline documents={profile.documents} />
                <ConsistencyRadarChart result={analysis} />
                <DriftChart result={analysis} />
              </div>

              <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
                <EmbeddingCluster points={clusterPoints} />
                <DiffHighlight result={analysis} />
              </div>
            </div>
          ) : null}
        </section>
      </div>
    </main>
  );
}

function ProfileMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-border bg-panelSoft p-3">
      <div className="text-xs text-muted">{label}</div>
      <div className="mt-1 truncate text-sm font-medium">{value}</div>
    </div>
  );
}
