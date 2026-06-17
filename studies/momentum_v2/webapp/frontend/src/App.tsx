import React, { useEffect, useMemo, useState } from "react";
import { api } from "./api";
import { ContributionBars, LineChart, type Line } from "./charts";
import type {
  ContributionRow,
  CurrentPortfolio,
  HistoryEvent,
  Meta,
  Methodologies,
  SeriesPoint,
  StrategyIndex,
} from "./types";
import { colorFor, Disclaimer, fmtNum, fmtPct, GateBadge, Spinner, Stat } from "./ui";

const UNIVERSE = "us_stocks";

function useAsync<T>(fn: () => Promise<T>, deps: React.DependencyList): { data: T | null; err: string | null; loading: boolean } {
  const [state, setState] = useState<{ data: T | null; err: string | null; loading: boolean }>({ data: null, err: null, loading: true });
  useEffect(() => {
    let live = true;
    setState({ data: null, err: null, loading: true });
    fn().then(
      (data) => live && setState({ data, err: null, loading: false }),
      (e) => live && setState({ data: null, err: String(e), loading: false }),
    );
    return () => { live = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  return state;
}

const toX = (s: SeriesPoint[]): number[] => s.map((p) => new Date(String(p.date)).getTime() / 1000);
const col = (s: SeriesPoint[], k: string): (number | null)[] => s.map((p) => (typeof p[k] === "number" ? (p[k] as number) : null));

export default function App() {
  const [window, setWindow] = useState<string>("");
  const [view, setView] = useState<"overview" | "detail" | "methodology">("overview");
  const [selected, setSelected] = useState<string | null>(null);

  const windows = useAsync(() => api.windows(UNIVERSE), []);
  useEffect(() => {
    if (windows.data && windows.data.windows.length && !window) setWindow(windows.data.windows[0]);
  }, [windows.data, window]);

  const index = useAsync(() => api.strategies(UNIVERSE, window), [window]);

  const open = (name: string) => { setSelected(name); setView("detail"); };

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand" onClick={() => setView("overview")} role="button">
          <span className="brand-dot" /> Momentum Portfolio <span className="brand-sub">research</span>
        </div>
        <nav className="nav">
          <button className={view === "overview" ? "on" : ""} onClick={() => setView("overview")}>Strategies</button>
          <button className={view === "methodology" ? "on" : ""} onClick={() => setView("methodology")}>Methodology</button>
        </nav>
        <div className="winsel">
          <label>window</label>
          <select value={window} onChange={(e) => { setWindow(e.target.value); setView("overview"); }}>
            {(windows.data?.windows ?? []).map((w) => <option key={w} value={w}>{w}</option>)}
          </select>
        </div>
      </header>

      {index.data && <Disclaimer text={index.data.disclaimer} />}

      <main className="content">
        {view === "methodology" ? (
          <MethodologyView />
        ) : view === "detail" && selected ? (
          <DetailView name={selected} window={window} onBack={() => setView("overview")} />
        ) : index.loading ? (
          <Spinner label="Loading strategies…" />
        ) : index.err ? (
          <ErrorBox msg={index.err} hint="Run the funnel + portfolio_export.py for this window first." />
        ) : index.data ? (
          <OverviewView index={index.data} window={window} onOpen={open} />
        ) : null}
      </main>

      <footer className="foot">
        momentum_v2 · promotion_eligible=false · not investment advice
      </footer>
    </div>
  );
}

function ErrorBox({ msg, hint }: { msg: string; hint?: string }) {
  return <div className="errorbox"><strong>Couldn’t load.</strong> {msg}{hint ? <div className="muted">{hint}</div> : null}</div>;
}

// --- Overview / compare -----------------------------------------------------

type SortKey = "rolling" | "cagr" | "sharpe" | "mdd";

function OverviewView({ index, window, onOpen }: { index: StrategyIndex; window: string; onOpen: (n: string) => void }) {
  const [sort, setSort] = useState<SortKey>("cagr");
  const [picked, setPicked] = useState<string[]>(index.strategies.slice(0, 3).map((s) => s.name));

  const sorted = useMemo(() => {
    const rows = [...index.strategies];
    const key = sort === "mdd" ? (r: typeof rows[number]) => -r.mdd : (r: typeof rows[number]) => (sort === "rolling" ? r.cagr : r[sort]);
    return rows.sort((a, b) => key(b) - key(a));
  }, [index.strategies, sort]);

  const toggle = (name: string) =>
    setPicked((p) => (p.includes(name) ? p.filter((n) => n !== name) : [...p, name].slice(-6)));

  return (
    <>
      <div className="section-head">
        <h1>Strategies <span className="muted">· {index.universe} · {window} · vs {index.benchmark}</span></h1>
        <div className="muted">{index.strategies.length} strategies. After-tax (BR 15%), gross of costs.</div>
      </div>

      <EquityOverlay names={picked} window={window} benchmark={index.benchmark} />

      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th></th><th>Strategy</th><th>Mechanism</th><th>Top-N</th><th>Reb</th>
              <Th label="CAGR" k="cagr" sort={sort} set={setSort} />
              <Th label="MDD" k="mdd" sort={sort} set={setSort} />
              <Th label="Sharpe" k="sharpe" sort={sort} set={setSort} />
              <th>Gates</th><th>As of</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((s) => (
              <tr key={s.name} className="row">
                <td><input type="checkbox" checked={picked.includes(s.name)} onChange={() => toggle(s.name)} /></td>
                <td className="mono link" onClick={() => onOpen(s.name)}>{s.name}</td>
                <td>{s.mechanism}</td>
                <td>{s.top_n}</td>
                <td>{s.rebalance_months}m</td>
                <td className="num pos">{fmtPct(s.cagr)}</td>
                <td className="num neg">{fmtPct(s.mdd)}</td>
                <td className="num">{fmtNum(s.sharpe)}</td>
                <td><GateBadge pass={s.gate_pass} /></td>
                <td className="muted">{s.as_of ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

function Th({ label, k, sort, set }: { label: string; k: SortKey; sort: SortKey; set: (k: SortKey) => void }) {
  return <th className={`sortable ${sort === k ? "active" : ""}`} onClick={() => set(k)}>{label}{sort === k ? " ▼" : ""}</th>;
}

function EquityOverlay({ names, window, benchmark }: { names: string[]; window: string; benchmark: string }) {
  const all = useAsync(async () => {
    const series = await Promise.all(names.map((n) => api.series(n, UNIVERSE, window).then((s) => ({ n, s })).catch(() => null)));
    return series.filter(Boolean) as { n: string; s: SeriesPoint[] }[];
  }, [names.join(","), window]);

  if (!names.length) return <div className="card muted">Select strategies below to overlay their equity curves.</div>;
  if (all.loading) return <div className="card"><Spinner label="Loading curves…" /></div>;
  if (!all.data || !all.data.length) return <div className="card muted">No series available.</div>;

  const ref = all.data[0].s;
  const x = toX(ref);
  const lines: Line[] = all.data.map((d, i) => ({ label: d.n.replace(/^momv2_us_stocks_/, ""), y: col(d.s, "equity_after_tax"), color: colorFor(i) }));
  const benchEq = col(ref, `${benchmark.toLowerCase()}_equity`);
  if (benchEq.some((v) => v != null)) lines.push({ label: benchmark, y: benchEq, color: "#9ca3af" });

  return (
    <div className="card">
      <div className="card-title">Equity (log) — $1 after-tax, vs {benchmark}</div>
      <LineChart x={x} lines={lines} height={320} logY />
    </div>
  );
}

// --- Detail -----------------------------------------------------------------

function DetailView({ name, window, onBack }: { name: string; window: string; onBack: () => void }) {
  const meta = useAsync(() => api.meta(name, UNIVERSE, window), [name, window]);
  const cur = useAsync(() => api.current(name, UNIVERSE, window), [name, window]);
  const hist = useAsync(() => api.history(name, UNIVERSE, window), [name, window]);
  const contrib = useAsync(() => api.contribution(name, UNIVERSE, window), [name, window]);
  const series = useAsync(() => api.series(name, UNIVERSE, window), [name, window]);
  const meth = useAsync(() => api.methodologies(), []);

  return (
    <>
      <button className="back" onClick={onBack}>← all strategies</button>
      {meta.loading ? <Spinner /> : meta.err ? <ErrorBox msg={meta.err} /> : meta.data ? (
        <DetailBody meta={meta.data} cur={cur.data} hist={hist.data} contrib={contrib.data} series={series.data} meth={meth.data} />
      ) : null}
    </>
  );
}

function DetailBody({ meta, cur, hist, contrib, series, meth }: {
  meta: Meta; cur: CurrentPortfolio | null; hist: HistoryEvent[] | null;
  contrib: ContributionRow[] | null; series: SeriesPoint[] | null; meth: Methodologies | null;
}) {
  const m = meta.metrics;
  const gate = meta.gate_verdict;
  const explain = meth?.score_modes?.[meta.score_mode ?? ""] ?? "";

  return (
    <>
      <div className="section-head">
        <h1 className="mono">{meta.name}</h1>
        <div className="row-wrap">
          <span className="tag">{meta.mechanism}</span>
          <span className="tag">top {meta.top_n}</span>
          <span className="tag">reb {meta.rebalance_months}m</span>
          <span className="tag">{meta.weight_mode}</span>
          {gate ? <GateBadge pass={Boolean((gate as Record<string, unknown>).all_pass)} /> : null}
        </div>
        {explain ? <p className="explain">{explain} {meth?.scoring}</p> : null}
      </div>

      <div className="stats">
        <Stat label="CAGR (after-tax)" value={fmtPct(m.after_tax_cagr ?? m.cagr)} accent="pos" />
        <Stat label="Max drawdown" value={fmtPct(m.after_tax_mdd ?? m.mdd)} accent="neg" />
        <Stat label="Sharpe" value={fmtNum(m.after_tax_sharpe ?? m.sharpe)} />
        <Stat label="Calmar" value={fmtNum(m.after_tax_calmar ?? m.calmar)} />
        <Stat label="Rolling dominance" value={fmtPct(m.rolling_rel_score)} />
        <Stat label="Excess vs SPY" value={fmtPct(m.excess_cagr)} />
        <Stat label="Annual turnover" value={fmtNum(m.annual_turnover)} />
        <Stat label="Rebalances" value={meta.n_rebalances ?? "—"} />
      </div>

      {series && series.length ? (
        <div className="grid2">
          <div className="card">
            <div className="card-title">Equity (log) — $1 after-tax vs benchmarks</div>
            <EquityCard series={series} />
          </div>
          <div className="card">
            <div className="card-title">Drawdown</div>
            <DrawdownCard series={series} />
          </div>
        </div>
      ) : null}

      <div className="grid2">
        <div className="card">
          <div className="card-title">Current portfolio {cur?.as_of ? <span className="muted">· as of {cur.as_of}</span> : null}</div>
          {cur ? <HoldingsTable holdings={cur.holdings} /> : <Spinner />}
        </div>
        <div className="card">
          <div className="card-title">Top contributors</div>
          {contrib ? <ContributionBars rows={[...contrib.slice(0, 8), ...contrib.slice(-4)]} /> : <Spinner />}
        </div>
      </div>

      <div className="card">
        <div className="card-title">Holdings history — entries & exits</div>
        {hist ? <HistoryTimeline events={hist} /> : <Spinner />}
      </div>

      {gate ? <GateCard verdict={gate as Record<string, unknown>} /> : null}
    </>
  );
}

function EquityCard({ series }: { series: SeriesPoint[] }) {
  const x = toX(series);
  const lines: Line[] = [{ label: "after-tax", y: col(series, "equity_after_tax"), color: colorFor(0) }];
  for (const [k, label, c] of [["spy_equity", "SPY", "#9ca3af"], ["spmo_equity", "SPMO", "#fbbf24"]] as const) {
    const y = col(series, k);
    if (y.some((v) => v != null)) lines.push({ label, y, color: c });
  }
  return <LineChart x={x} lines={lines} height={300} logY />;
}

function DrawdownCard({ series }: { series: SeriesPoint[] }) {
  const eq = col(series, "equity_after_tax");
  let peak = -Infinity;
  const dd = eq.map((v) => { if (v == null) return null; peak = Math.max(peak, v); return v / peak - 1; });
  return <LineChart x={toX(series)} lines={[{ label: "drawdown", y: dd, color: "#f87171" }]} height={200} />;
}

function HoldingsTable({ holdings }: { holdings: { ticker: string; weight: number }[] }) {
  if (!holdings.length) return <div className="muted">No active holdings.</div>;
  return (
    <table className="table compact">
      <thead><tr><th>Ticker</th><th>Weight</th></tr></thead>
      <tbody>{holdings.map((h) => (
        <tr key={h.ticker}><td className="mono">{h.ticker}</td>
          <td><span className="wbar"><span style={{ width: `${h.weight * 100}%` }} /></span>{fmtPct(h.weight)}</td></tr>
      ))}</tbody>
    </table>
  );
}

function HistoryTimeline({ events }: { events: HistoryEvent[] }) {
  const recent = [...events].reverse();
  return (
    <div className="timeline">
      {recent.map((e) => (
        <div className="tl-row" key={e.date}>
          <span className="tl-date mono">{e.date}</span>
          <span className="tl-count">{e.holdings.length} held</span>
          <span className="tl-chips">
            {e.entered.map((t) => <span className="chip in" key={"in" + t}>+{t}</span>)}
            {e.exited.map((t) => <span className="chip out" key={"out" + t}>−{t}</span>)}
            {!e.entered.length && !e.exited.length ? <span className="muted">no change</span> : null}
          </span>
        </div>
      ))}
    </div>
  );
}

function GateCard({ verdict }: { verdict: Record<string, unknown> }) {
  const items: [string, boolean][] = [
    ["DSR p<0.05", Boolean(verdict.dsr_pass)],
    ["WF ≥6/8", Boolean(verdict.wf_pass)],
    ["Bootstrap CI>0", Boolean(verdict.bootstrap_pass)],
    ["xlib ±3pp", Boolean(verdict.xlib_pass)],
  ];
  return (
    <div className="card">
      <div className="card-title">Honest gates (validate phase)</div>
      <div className="row-wrap">
        {items.map(([l, ok]) => <span key={l} className={`gatepill ${ok ? "ok" : "no"}`}>{ok ? "✓" : "✕"} {l}</span>)}
      </div>
      <p className="muted">A FAIL is the expected, honest outcome for a survivorship-biased screen — not a defect.</p>
    </div>
  );
}

// --- Methodology ------------------------------------------------------------

function MethodologyView() {
  const meth = useAsync(() => api.methodologies(), []);
  if (meth.loading) return <Spinner />;
  if (!meth.data) return <ErrorBox msg={meth.err ?? "unavailable"} />;
  const m = meth.data;
  return (
    <>
      <div className="section-head"><h1>Methodology</h1></div>
      <div className="card">
        <div className="card-title">Scoring — the rolling-dominance lens</div>
        <p className="explain">{m.scoring}</p>
        <p className="explain"><strong>Weighting.</strong> {m.weighting}</p>
        <p className="explain"><strong>Rebalance.</strong> {m.rebalance}</p>
      </div>
      <div className="card">
        <div className="card-title">Score modes</div>
        {Object.entries(m.score_modes).map(([k, v]) => (
          <p className="explain" key={k}><span className="mono">{k}</span> — {v}</p>
        ))}
      </div>
      <div className="card">
        <div className="card-title">Honest gates</div>
        <p className="explain">{String((m.gates as Record<string, unknown>).summary ?? "")}</p>
        {Object.entries(m.gates).filter(([k]) => k !== "summary").map(([k, v]) => (
          <p className="explain" key={k}><span className="mono">{k}</span> — {String(v)}</p>
        ))}
      </div>
      <Disclaimer text={m.disclaimer} />
    </>
  );
}
