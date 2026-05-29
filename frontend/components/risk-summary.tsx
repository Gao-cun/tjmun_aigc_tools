"use client";

import { Activity, AlertTriangle, CheckCircle2 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import type { AnalysisResult } from "@/lib/types";
import { cn } from "@/lib/utils";

export function RiskSummary({ result }: { result?: AnalysisResult | null }) {
  const level = result?.riskLevel ?? "No analysis yet";
  const isHigh = level.startsWith("High");
  const isMedium = level.startsWith("Medium");
  const displayLevel = !result ? "尚未分析" : isHigh ? "高一致性风险" : isMedium ? "中一致性风险" : "低一致性风险";
  const Icon = isHigh ? AlertTriangle : isMedium ? Activity : CheckCircle2;

  return (
    <Card className="min-h-[210px]">
      <CardHeader>
        <CardTitle>一致性风险</CardTitle>
        <Badge className={cn(isHigh && "border-danger text-danger", isMedium && "border-warning text-warning", !isHigh && !isMedium && "border-success text-success")}>
          {displayLevel}
        </Badge>
      </CardHeader>
      <div className="flex items-center gap-4">
        <div className={cn("flex h-14 w-14 items-center justify-center rounded-lg bg-panelSoft", isHigh && "text-danger", isMedium && "text-warning", !isHigh && !isMedium && "text-success")}>
          <Icon className="h-7 w-7" />
        </div>
        <div>
          <div className="text-3xl font-semibold">{result ? result.historicalDeviation.toFixed(2) : "—"}</div>
          <p className="mt-1 text-sm text-muted">历史偏离指数</p>
        </div>
      </div>
      <div className="mt-5 grid grid-cols-2 gap-3 text-sm">
        <Metric label="风格计量偏移" value={result?.stylometricShift} />
        <Metric label="语义漂移" value={result?.semanticDrift} />
      </div>
    </Card>
  );
}

function Metric({ label, value }: { label: string; value?: number }) {
  return (
    <div className="rounded-md border border-border bg-panelSoft p-3">
      <div className="text-lg font-medium">{value === undefined ? "—" : value.toFixed(3)}</div>
      <div className="text-xs text-muted">{label}</div>
    </div>
  );
}
