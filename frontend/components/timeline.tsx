"use client";

import { FileText } from "lucide-react";

import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import type { HistoryDocument } from "@/lib/types";
import { cn } from "@/lib/utils";

export function Timeline({ documents }: { documents: HistoryDocument[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>历史风格时间线</CardTitle>
      </CardHeader>
      <div className="space-y-3">
        {documents.length === 0 ? <p className="text-sm text-muted">还没有历史文件。</p> : null}
        {documents.map((doc) => (
          <div key={doc.id} className="flex items-center gap-3 rounded-md border border-border bg-panelSoft p-3">
            <FileText className="h-4 w-4 text-accent" />
            <div className="min-w-0 flex-1">
              <div className="truncate text-sm font-medium">{doc.filename}</div>
              <div className="text-xs text-muted">{doc.documentType} · {doc.meeting ?? "未填写会议"} · {doc.documentDate ?? "未填写日期"}</div>
              {doc.errorMessage ? <div className="mt-2 line-clamp-3 text-xs leading-5 text-danger">{doc.errorMessage}</div> : null}
            </div>
            <span className={cn("rounded-md px-2 py-1 text-xs", doc.status === "ready" ? "bg-success/10 text-success" : doc.status === "failed" ? "bg-danger/10 text-danger" : "bg-warning/10 text-warning")}>
              {doc.status}
            </span>
          </div>
        ))}
      </div>
    </Card>
  );
}
