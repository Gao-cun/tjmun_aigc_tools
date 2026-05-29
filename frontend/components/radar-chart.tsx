"use client";

import { PolarAngleAxis, PolarGrid, Radar, RadarChart as ReRadarChart, ResponsiveContainer, Tooltip } from "recharts";

import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import type { AnalysisResult } from "@/lib/types";

export function ConsistencyRadarChart({ result }: { result?: AnalysisResult | null }) {
  const data = result?.radar ?? [];
  return (
    <Card>
      <CardHeader>
        <CardTitle>风格偏离雷达图</CardTitle>
      </CardHeader>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <ReRadarChart data={data}>
            <PolarGrid stroke="rgba(148, 163, 184, 0.2)" />
            <PolarAngleAxis dataKey="feature" tick={{ fill: "#CBD5E1", fontSize: 11 }} />
            <Tooltip contentStyle={{ background: "#0E1118", border: "1px solid rgba(148, 163, 184, 0.18)", color: "#F4F7FB" }} />
            <Radar name="历史基线" dataKey="baseline" stroke="#8993A5" fill="#8993A5" fillOpacity={0.18} />
            <Radar name="本次文本" dataKey="current" stroke="#56C2FF" fill="#56C2FF" fillOpacity={0.28} />
          </ReRadarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
