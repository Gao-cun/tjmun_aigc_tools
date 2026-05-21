"use client";

import { Scatter, ScatterChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import type { ClusterPoint } from "@/lib/types";

export function EmbeddingCluster({ points }: { points: ClusterPoint[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Embedding Cluster</CardTitle>
      </CardHeader>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart>
            <CartesianGrid stroke="rgba(148, 163, 184, 0.12)" />
            <XAxis type="number" dataKey="x" name="x" tick={{ fill: "#CBD5E1", fontSize: 11 }} />
            <YAxis type="number" dataKey="y" name="y" tick={{ fill: "#CBD5E1", fontSize: 11 }} />
            <Tooltip cursor={{ strokeDasharray: "3 3" }} contentStyle={{ background: "#0E1118", border: "1px solid rgba(148, 163, 184, 0.18)", color: "#F4F7FB" }} />
            <Scatter name="Documents" data={points} fill="#56C2FF" />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}

