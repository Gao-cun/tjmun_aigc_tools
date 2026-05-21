"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import type { AnalysisResult } from "@/lib/types";

export function DriftChart({ result }: { result?: AnalysisResult | null }) {
  const data = (result?.featureDrift ?? []).map((item) => ({
    ...item,
    short: item.feature.split(".").slice(-1)[0]
  }));
  return (
    <Card>
      <CardHeader>
        <CardTitle>Feature Drift</CardTitle>
      </CardHeader>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid stroke="rgba(148, 163, 184, 0.12)" vertical={false} />
            <XAxis dataKey="short" tick={{ fill: "#CBD5E1", fontSize: 11 }} />
            <YAxis tick={{ fill: "#CBD5E1", fontSize: 11 }} />
            <Tooltip contentStyle={{ background: "#0E1118", border: "1px solid rgba(148, 163, 184, 0.18)", color: "#F4F7FB" }} />
            <Bar dataKey="zScore" fill="#56C2FF" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}

