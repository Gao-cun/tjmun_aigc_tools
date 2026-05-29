"use client";

import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import type { AnalysisResult } from "@/lib/types";

export function DiffHighlight({ result }: { result?: AnalysisResult | null }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>显著变化特征</CardTitle>
      </CardHeader>
      <div className="space-y-2">
        {(result?.significantFeatures ?? []).length === 0 ? <p className="text-sm text-muted">完成一次分析后，这里会显示偏离最明显的写作特征。</p> : null}
        {(result?.significantFeatures ?? []).map((item) => (
          <div key={item.feature} className="rounded-md border border-border bg-panelSoft p-3">
            <div className="text-sm font-medium">{item.feature}</div>
            <div className="mt-1 text-xs text-muted">相对历史基线的 z-score 偏离：{item.zScore.toFixed(2)}</div>
          </div>
        ))}
      </div>
    </Card>
  );
}
