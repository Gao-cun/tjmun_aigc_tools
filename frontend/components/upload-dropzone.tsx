"use client";

import { useCallback, useState } from "react";
import { FileUp, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import type { AnalyzeResponse, EmbeddingSettings } from "@/lib/types";
import { cn } from "@/lib/utils";

type UploadDropzoneProps = {
  delegateId?: string;
  mode: "history" | "analysis";
  embeddingSettings: EmbeddingSettings;
  onUploaded?: () => void;
  onAnalyzed?: (response: AnalyzeResponse) => void;
};

export function UploadDropzone({ delegateId, mode, embeddingSettings, onUploaded, onAnalyzed }: UploadDropzoneProps) {
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [documentType, setDocumentType] = useState("Position Paper");
  const [meeting, setMeeting] = useState("TJMUN");
  const [documentDate, setDocumentDate] = useState("");
  const [status, setStatus] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const pickFile = useCallback((items: FileList | null) => {
    const next = items?.[0];
    if (next) {
      setFile(next);
      setStatus("");
    }
  }, []);

  async function submit() {
    if (!delegateId || !file) {
      setStatus("请先选择代表和文件。");
      return;
    }
    setLoading(true);
    setStatus("");
    const form = new FormData();
    form.append("delegate_id", delegateId);
    form.append("file", file);
    form.append("embedding_provider", embeddingSettings.embeddingProvider);
    form.append("local_embedding_model", embeddingSettings.localEmbeddingModel);
    form.append("openai_embedding_model", embeddingSettings.openaiEmbeddingModel);
    if (embeddingSettings.openaiApiKey) {
      form.append("openai_api_key", embeddingSettings.openaiApiKey);
    }
    if (mode === "history") {
      form.append("document_type", documentType);
      form.append("meeting", meeting);
      if (documentDate) form.append("document_date", documentDate);
    }
    try {
      if (mode === "history") {
        await api.uploadHistory(form);
        setStatus("历史文件已进入后台处理队列。");
        setFile(null);
        setTimeout(() => onUploaded?.(), 900);
      } else {
        const response = await api.analyze(form);
        onAnalyzed?.(response);
        setStatus("分析完成。");
      }
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "上传失败。");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-3">
      <div
        className={cn(
          "flex min-h-[150px] cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-border bg-panelSoft p-5 text-center transition-colors",
          dragging && "border-accent bg-sky-950/20"
        )}
        onDragOver={(event) => {
          event.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(event) => {
          event.preventDefault();
          setDragging(false);
          pickFile(event.dataTransfer.files);
        }}
      >
        <FileUp className="mb-3 h-8 w-8 text-accent" />
        <div className="text-sm font-medium">{file ? file.name : mode === "history" ? "拖拽上传历史写作文件" : "拖拽上传待分析新文本"}</div>
        <div className="mt-1 text-xs text-muted">支持 txt、docx、pdf</div>
        <input className="mt-4 text-xs text-muted" type="file" accept=".txt,.docx,.pdf" onChange={(event) => pickFile(event.target.files)} />
      </div>

      {mode === "history" ? (
        <div className="grid grid-cols-1 gap-2 md:grid-cols-3">
          <input className="rounded-md border border-border bg-panelSoft px-3 py-2 text-sm outline-none focus:border-accent" value={documentType} onChange={(event) => setDocumentType(event.target.value)} placeholder="文件类型" />
          <input className="rounded-md border border-border bg-panelSoft px-3 py-2 text-sm outline-none focus:border-accent" value={meeting} onChange={(event) => setMeeting(event.target.value)} placeholder="会议名称" />
          <input className="rounded-md border border-border bg-panelSoft px-3 py-2 text-sm outline-none focus:border-accent" type="date" value={documentDate} onChange={(event) => setDocumentDate(event.target.value)} />
        </div>
      ) : null}

      <div className="flex items-center justify-between gap-3">
        <p className="text-xs text-muted">{status}</p>
        <Button onClick={submit} disabled={loading || !file || !delegateId}>
          {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
          {mode === "history" ? "上传历史文件" : "开始一致性分析"}
        </Button>
      </div>
    </div>
  );
}
