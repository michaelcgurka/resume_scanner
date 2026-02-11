import React from "react";
import {
  RadialBarChart,
  RadialBar,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from "recharts";

const GAUGE_COLORS = {
  low: "#ef4444",   // red < 40
  mid: "#eab308",   // yellow 40-70
  high: "#14b8a6",
};

function getGaugeColor(valuePct) {
  if (valuePct < 40) return GAUGE_COLORS.low;
  if (valuePct < 70) return GAUGE_COLORS.mid;
  return GAUGE_COLORS.high;
}

function ScoreGauge({ score }) {
  const valuePct = Math.round((Number(score) || 0) * 100);
  const fill = getGaugeColor(valuePct);
  const data = [{ name: "Match", value: valuePct, fill }];
  return (
    <div className="w-full max-w-[220px] mx-auto relative">
      <ResponsiveContainer width="100%" height={180}>
        <RadialBarChart
          innerRadius="70%"
          outerRadius="100%"
          barSize={14}
          data={data}
          startAngle={180}
          endAngle={0}
        >
          <RadialBar background minAngle={0} dataKey="value" />
        </RadialBarChart>
      </ResponsiveContainer>
      <div
        className="absolute inset-0 flex items-center justify-center pointer-events-none"
        style={{ bottom: "20%" }}
      >
        <span className="text-2xl font-semibold text-gray-900 dark:text-gray-100">
          {valuePct}%
        </span>
      </div>
      <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-0">Overall match</p>
    </div>
  );
}

const BREAKDOWN_COLORS = ["#6366f1", "#8b5cf6", "#14b8a6"];

function BreakdownBars({ breakdown }) {
  if (!breakdown) return null;
  const data = [
    { name: "Semantic", value: Math.round((breakdown.semantic ?? 0) * 100) },
    { name: "Keyword", value: Math.round((breakdown.keyword ?? 0) * 100) },
    { name: "Structure", value: Math.round((breakdown.structure ?? 0) * 100) },
  ];
  return (
    <div className="w-full mt-4">
      <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Score breakdown</p>
      <ResponsiveContainer width="100%" height={160}>
        <BarChart data={data} layout="vertical" margin={{ left: 8, right: 8 }}>
          <XAxis type="number" domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
          <YAxis type="category" dataKey="name" width={70} tick={{ fontSize: 12 }} />
          <Tooltip formatter={(v) => [`${v}%`, "Score"]} />
          <Bar dataKey="value" radius={4}>
            {data.map((_, i) => (
              <Cell key={i} fill={BREAKDOWN_COLORS[i % BREAKDOWN_COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function ScoreVisualizer({ score, breakdown }) {
  return (
    <div className="flex flex-col items-center">
      <ScoreGauge score={score} />
      <BreakdownBars breakdown={breakdown} />
    </div>
  );
}
