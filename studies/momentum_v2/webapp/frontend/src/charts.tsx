import React, { useEffect, useRef } from "react";
import uPlot from "uplot";

export interface Line {
  label: string;
  y: (number | null)[];
  color: string;
}

/** Minimal responsive uPlot line chart. Recreates on prop change (simple + correct). */
export function LineChart({
  x,
  lines,
  height = 280,
  logY = false,
}: {
  x: number[];
  lines: Line[];
  height?: number;
  logY?: boolean;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const plot = useRef<uPlot | null>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el || x.length === 0) return;
    const data = [x, ...lines.map((l) => l.y)] as unknown as uPlot.AlignedData;
    const axis = { stroke: "#8b909b", grid: { stroke: "rgba(255,255,255,0.06)" }, ticks: { stroke: "rgba(255,255,255,0.10)" } };
    const opts: uPlot.Options = {
      width: el.clientWidth || 640,
      height,
      scales: { x: { time: true }, y: { distr: logY ? 3 : 1 } },
      legend: { show: true },
      cursor: { points: { size: 6 } },
      series: [{}, ...lines.map((l) => ({ label: l.label, stroke: l.color, width: 2, points: { show: false } }))],
      axes: [axis, axis],
    };
    plot.current = new uPlot(opts, data, el);
    const ro = new ResizeObserver(() => plot.current?.setSize({ width: el.clientWidth, height }));
    ro.observe(el);
    return () => {
      ro.disconnect();
      plot.current?.destroy();
      plot.current = null;
    };
  }, [x, lines, height, logY]);

  return <div ref={ref} className="chart" />;
}

/** Bars for per-ticker contribution (positive teal / negative red). */
export function ContributionBars({ rows }: { rows: { ticker: string; contribution: number }[] }) {
  const max = Math.max(1e-9, ...rows.map((r) => Math.abs(r.contribution)));
  return (
    <div className="bars">
      {rows.map((r) => (
        <div className="bar-row" key={r.ticker}>
          <span className="bar-tick">{r.ticker}</span>
          <span className="bar-track">
            <span
              className={`bar-fill ${r.contribution >= 0 ? "pos" : "neg"}`}
              style={{ width: `${(Math.abs(r.contribution) / max) * 100}%` }}
            />
          </span>
          <span className="bar-val">{(r.contribution * 100).toFixed(1)}%</span>
        </div>
      ))}
    </div>
  );
}
