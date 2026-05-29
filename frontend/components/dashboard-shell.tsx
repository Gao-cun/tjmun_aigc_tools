"use client";

import { useEffect, useMemo, useState } from "react";
import { Database, FlaskConical, Plus, RefreshCw, Settings2 } from "lucide-react";

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
import type { AnalysisResult, ClusterPoint, Delegate, DelegateProfile, EmbeddingSettings } from "@/lib/types";
import { cn } from "@/lib/utils";

export function DashboardShell({ initialDelegateId }: { initialDelegateId?: string }) {
  const [delegates, setDelegates] = useState<Delegate[]>([]);
  const [selectedId, setSelectedId] = useState<string | undefined>(initialDelegateId);
  const [profile, setProfile] = useState<DelegateProfile | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [newDelegateName, setNewDelegateName] = useState("");
  const [embeddingSettings, setEmbeddingSettings] = useState<EmbeddingSettings>({
    embeddingProvider: "hash",
    localEmbeddingModel: "sentence-transformers/all-MiniLM-L6-v2",
    openaiEmbeddingModel: "text-embedding-3-small",
    openaiApiKey: ""
  });

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
      setMessage(error instanceof Error ? error.message : "无法加载工作区。");
    } finally {
      setLoading(false);
    }
  }

  async function createDelegate() {
    if (!newDelegateName.trim()) return;
    const delegate = await api.createDelegate({ name: newDelegateName.trim(), country: "未分配", committee: "大会" });
    setNewDelegateName("");
    await refreshDelegates(delegate.id);
  }

  useEffect(() => {
    const saved = window.localStorage.getItem("dwca.embeddingSettings");
    if (saved) {
      try {
        setEmbeddingSettings((current) => ({ ...current, ...JSON.parse(saved) }));
      } catch {
        window.localStorage.removeItem("dwca.embeddingSettings");
      }
    }
    void refreshDelegates(initialDelegateId);
    // 初次加载即可，后续切换通过显式 handler 控制。
  }, [initialDelegateId]);

  useEffect(() => {
    window.localStorage.setItem("dwca.embeddingSettings", JSON.stringify({ ...embeddingSettings, openaiApiKey: "" }));
  }, [embeddingSettings]);

  async function switchDelegate(delegateId: string) {
    setSelectedId(delegateId);
    setAnalysis(null);
    setProfile(await api.getProfile(delegateId));
  }

  const clusterPoints = useMemo<ClusterPoint[]>(() => {
    const base = profile?.embedding_stats?.cluster_points ?? [];
    if (!analysis) return base;
    return [...base, { label: "本次分析", x: analysis.semanticDrift, y: analysis.stylometricShift, kind: "analysis" }];
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
              <div className="text-sm font-semibold">写作一致性</div>
              <div className="text-xs text-muted">研究分析平台</div>
            </div>
          </div>

          <div className="space-y-2">
            <div className="text-xs uppercase tracking-[0.14em] text-muted">代表档案</div>
            {delegates.map((delegate) => (
              <button
                key={delegate.id}
                className={cn("w-full rounded-md border border-transparent px-3 py-3 text-left text-sm transition-colors hover:bg-panelSoft", selectedId === delegate.id && "border-border bg-panelSoft")}
                onClick={() => void switchDelegate(delegate.id)}
              >
                <div className="font-medium">{delegate.name}</div>
                <div className="text-xs text-muted">{delegate.committee ?? "未设置委员会"} · {delegate.document_count} 篇历史文件</div>
              </button>
            ))}
          </div>

          <div className="mt-auto space-y-2">
            <input className="w-full rounded-md border border-border bg-panelSoft px-3 py-2 text-sm outline-none focus:border-accent" value={newDelegateName} onChange={(event) => setNewDelegateName(event.target.value)} placeholder="新代表姓名" />
            <Button className="w-full" variant="secondary" onClick={() => void createDelegate()}>
              <Plus className="mr-2 h-4 w-4" />
              创建档案
            </Button>
          </div>
        </aside>

        <section className="min-w-0 flex-1">
          <header className="mb-6 flex flex-col gap-4 border-b border-border pb-5 md:flex-row md:items-end md:justify-between">
            <div>
              <div className="mb-2 flex items-center gap-2">
                <Badge>一致性分析</Badge>
                <Badge>风格计量</Badge>
                <Badge>Embedding 基线</Badge>
              </div>
              <h1 className="text-3xl font-semibold tracking-normal">模联代表写作一致性分析器</h1>
              <p className="mt-2 max-w-3xl text-sm text-muted">用于比较新文本与代表历史写作画像之间的偏离程度，重点呈现风格漂移、语义漂移和修订过程异常指标，而不是输出“AI 率”。</p>
            </div>
            <Button variant="secondary" onClick={() => void refreshDelegates()}>
              <RefreshCw className="mr-2 h-4 w-4" />
              刷新
            </Button>
          </header>

          {message ? <div className="mb-4 rounded-md border border-warning/40 bg-warning/10 p-3 text-sm text-warning">{message}</div> : null}
          {loading ? <div className="rounded-lg border border-border bg-panel p-8 text-sm text-muted">正在加载工作区...</div> : null}

          {!loading && profile ? (
            <div className="grid gap-5">
              <div className="grid grid-cols-1 gap-5 xl:grid-cols-[1.1fr_0.9fr]">
                <Card>
                  <CardHeader>
                    <CardTitle>代表写作档案</CardTitle>
                    <Badge>{profile.delegate.document_count} 篇历史文件</Badge>
                  </CardHeader>
                  <div className="grid gap-4 md:grid-cols-4">
                    <ProfileMetric label="姓名" value={profile.delegate.name} />
                    <ProfileMetric label="国家/席位" value={profile.delegate.country ?? "—"} />
                    <ProfileMetric label="委员会" value={profile.delegate.committee ?? "—"} />
                    <ProfileMetric label="风格基线" value={profile.embedding_stats ? "已建立" : "待建立"} />
                  </div>
                </Card>
                <RiskSummary result={analysis} />
              </div>

              <EmbeddingSettingsPanel settings={embeddingSettings} onChange={setEmbeddingSettings} />

              <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle>上传历史写作样本</CardTitle>
                    <Database className="h-4 w-4 text-muted" />
                  </CardHeader>
                  <UploadDropzone delegateId={selectedId} mode="history" embeddingSettings={embeddingSettings} onUploaded={() => void refreshDelegates(selectedId)} />
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle>分析新文本</CardTitle>
                    <FlaskConical className="h-4 w-4 text-muted" />
                  </CardHeader>
                  <UploadDropzone delegateId={selectedId} mode="analysis" embeddingSettings={embeddingSettings} onAnalyzed={(response) => setAnalysis(response.result)} />
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

function EmbeddingSettingsPanel({ settings, onChange }: { settings: EmbeddingSettings; onChange: (settings: EmbeddingSettings) => void }) {
  const update = (patch: Partial<EmbeddingSettings>) => onChange({ ...settings, ...patch });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Embedding 调用设置</CardTitle>
        <Settings2 className="h-4 w-4 text-muted" />
      </CardHeader>
      <div className="grid gap-3 lg:grid-cols-4">
        <label className="space-y-1 text-xs text-muted">
          Provider
          <select className="w-full rounded-md border border-border bg-panelSoft px-3 py-2 text-sm text-foreground outline-none focus:border-accent" value={settings.embeddingProvider} onChange={(event) => update({ embeddingProvider: event.target.value as EmbeddingSettings["embeddingProvider"] })}>
            <option value="hash">Hash 本地快速模式</option>
            <option value="local">HuggingFace 本地模型</option>
            <option value="openai">OpenAI Embedding API</option>
          </select>
        </label>
        <label className="space-y-1 text-xs text-muted lg:col-span-2">
          本地 HuggingFace 模型
          <input className="w-full rounded-md border border-border bg-panelSoft px-3 py-2 text-sm text-foreground outline-none focus:border-accent" value={settings.localEmbeddingModel} onChange={(event) => update({ localEmbeddingModel: event.target.value })} />
        </label>
        <label className="space-y-1 text-xs text-muted">
          OpenAI 模型
          <input className="w-full rounded-md border border-border bg-panelSoft px-3 py-2 text-sm text-foreground outline-none focus:border-accent" value={settings.openaiEmbeddingModel} onChange={(event) => update({ openaiEmbeddingModel: event.target.value })} />
        </label>
        <label className="space-y-1 text-xs text-muted lg:col-span-2">
          OpenAI API Key（仅本次浏览器会话使用，不保存）
          <input className="w-full rounded-md border border-border bg-panelSoft px-3 py-2 text-sm text-foreground outline-none focus:border-accent" type="password" value={settings.openaiApiKey} onChange={(event) => update({ openaiApiKey: event.target.value })} placeholder="sk-..." />
        </label>
        <div className="rounded-md border border-border bg-panelSoft p-3 text-xs leading-5 text-muted lg:col-span-2">
          上传历史样本和分析新文本必须使用同一类 provider/model；若向量维度不同，后端会拒绝分析以保护结果可信度。
        </div>
      </div>
    </Card>
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
