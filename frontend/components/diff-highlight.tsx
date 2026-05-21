"use client";

import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import type { AnalysisResult } from "@/lib/types";

export function DiffHighlight({ result }: { result?: AnalysisResult | null }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Significant Shifts</CardTitle>
      </CardHeader>
      <div className="space-y-2">
        {(result?.significantFeatures ?? []).length === 0 ? <p className="text-sm text-muted">Run an analysis to see feature-level deviations.</p> : null}
        {(result?.significantFeatures ?? []).map((item) => (
          <div key={item.feature} className="rounded-md border border-border bg-panelSoft p-3">
            <div className="text-sm font-medium">{item.feature}</div>
            <div className="mt-1 text-xs text-muted">z-score deviation {item.zScore.toFixed(2)} from historical baseline</div>
          </div>
        ))}
      </div>
    </Card>
  );
}

