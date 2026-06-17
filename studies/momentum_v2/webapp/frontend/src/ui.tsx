import React from "react";

export const fmtPct = (x: number | null | undefined, dp = 1): string =>
  x == null || Number.isNaN(x) ? "—" : `${(x * 100).toFixed(dp)}%`;

export const fmtNum = (x: number | null | undefined, dp = 2): string =>
  x == null || Number.isNaN(x) ? "—" : x.toFixed(dp);

export function GateBadge({ pass }: { pass: boolean }) {
  return (
    <span className={`badge ${pass ? "badge-pass" : "badge-fail"}`}>
      {pass ? "GATES PASS" : "GATES FAIL"}
    </span>
  );
}

export function Disclaimer({ text }: { text: string }) {
  return (
    <div className="disclaimer" role="note">
      <strong>Research only</strong> · {text}
    </div>
  );
}

export function Stat({ label, value, accent }: { label: string; value: React.ReactNode; accent?: "pos" | "neg" }) {
  return (
    <div className="stat">
      <div className="stat-label">{label}</div>
      <div className={`stat-value ${accent ?? ""}`}>{value}</div>
    </div>
  );
}

export function Spinner({ label }: { label?: string }) {
  return <div className="muted" style={{ padding: "2rem 0" }}>{label ?? "Loading…"}</div>;
}

const PALETTE = ["#5eead4", "#a78bfa", "#fbbf24", "#f472b6", "#60a5fa", "#34d399", "#f87171", "#c084fc"];
export const colorFor = (i: number): string => PALETTE[i % PALETTE.length];
