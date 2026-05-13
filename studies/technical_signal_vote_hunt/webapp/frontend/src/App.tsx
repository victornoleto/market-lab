import { useEffect, useMemo, useRef, useState } from 'react';
import type { MouseEvent } from 'react';
import { DayPicker } from 'react-day-picker';
import type { DateRange } from 'react-day-picker';
import 'react-day-picker/style.css';
import uPlot from 'uplot';
import type { MetricRow, ReportPayload, StrategiesPayload } from './types';

const palette = ['#0168fa', '#dc3545', '#00cccc', '#6f42c1', '#10b759', '#f59f00', '#f10075', '#5b47fb', '#7987a1', '#3b4863', '#00a3ff', '#b91c1c', '#0f766e', '#7c3aed', '#65a30d'];
const windows = [3, 5, 10, 15, 20];
type HeatHover = { x: number; y: number } | null;

const docs: Record<string, { concept: string; algorithm: string[]; status: string }> = {
  'iter030 T20D120 candidate': {
    concept: 'Performance-first sensitivity from the rearm family. It keeps the same Quad Risk K2 shell and changes only post-crash rearm geometry.',
    algorithm: ['Master ON/OFF shell: Quad Risk K2 vote on QLD with K=2 of 4 gates.', 'Gate 1: QLD close > QLD SMA250, a long-trend filter.', 'Gate 2: QLD close > QLD SMA100, a medium-trend filter.', 'Gate 3: QLD 21-day realised volatility < 40% annualized, a volatility-regime filter.', 'Gate 4: QLD 30-day AR(1) estimate > 0, a short persistence filter.', 'When the shell is ON, hold QLD by default.', 'If an OFF stretch lasted at least 20 trading days and the shell flips back ON, open a 120-trading-day rearm window.', 'During that T20D120 rearm window, upgrade the ON leg from QLD to TQQQ and apply the LRS1.20 overlay.', 'When the shell is OFF, hold ZROZ unless the rate-vol CASHX override is active.'],
    status: 'Best CAGR/terminal-equity sensitivity found here, but not a validated winner because strict validation failed DSR and PBO.',
  },
  'T20D90 balanced sensitivity': {
    concept: 'Balanced local T/D sensitivity. It tests whether the same faster crash trigger works with a less persistent D90 rearm window.',
    algorithm: ['Use the same Quad Risk K2 shell: QLD>SMA250, QLD>SMA100, RV21<40%, and AR1(30)>0, with K=2 required.', 'Keep the same QLD default ON leg, ZROZ defensive leg, rate-vol CASHX override, TQQQ upgrade and LRS1.20 overlay as Rearm T35D60.', 'Only the post-crash geometry changes: trigger after 20 OFF days and keep the TQQQ rearm window active for 90 trading days.'],
    status: 'Best balanced Sortino variant in the final local T/D grid; still research-only.',
  },
  'iter030 canonical': {
    concept: 'The canonical T35D60 rearm anchor from the LETF rotation study. It is the main core benchmark for this branch.',
    algorithm: ['Use the Quad Risk K2 shell: QLD close>SMA250, QLD close>SMA100, QLD RV21<40%, and QLD AR1(30)>0, with K=2 required.', 'When the shell is ON, hold QLD unless the post-crash rearm gate upgrades the ON leg.', 'The canonical rearm geometry is T35D60: trigger after at least 35 OFF days, then keep a 60-trading-day TQQQ upgrade window after OFF->ON.', 'Apply LRS1.20 to the ON leg.', 'When the shell is OFF, use ZROZ unless the rate-vol defensive override switches the off-leg to CASHX.'],
    status: 'Preserved as the core anchor because it remains strong and local improvements failed formal DSR/PBO validation.',
  },
  'T3d-K2 canonical': {
    concept: 'Four-gate risk shell. The name means it watches a quad of risk/regime filters and turns ON when any 2 of 4 pass.',
    algorithm: ['Compute four QLD-based gates.', 'Gate 1: QLD close > QLD SMA250 for long-horizon trend.', 'Gate 2: QLD close > QLD SMA100 for medium-horizon trend.', 'Gate 3: QLD 21-day realised volatility < 40% annualized for volatility control.', 'Gate 4: QLD 30-day AR(1) > 0 for return persistence.', 'Enter risk-on QLD when at least 2 of 4 gates pass.', 'Use ZROZ as the risk-off asset.', 'No TQQQ rearm turbo and no rearm-family rate-vol CASHX override.'],
    status: 'Lower CAGR than Rearm T35D60 but historically important as the frozen closed-study anchor.',
  },
  'Stage3 shared QLD': {
    concept: 'Eight-signal price-only vote on testfolio long-history data. The name means it watches an octet of price filters and turns ON when 6 of 8 pass.',
    algorithm: ['Build an 8-signal price-only vote on the underlying.', 'Signal 1: price > SMA10, a short trend filter.', 'Signal 2: price > EMA200, a long exponential-trend filter.', 'Signal 3: price > SMA250, a long simple-trend filter.', 'Signal 4: price > EMA250, a second long exponential-trend filter.', 'Signal 5: ROC20 > 0, one-month momentum.', 'Signal 6: ROC60 > 0, three-month momentum.', 'Signal 7: ROC120 > 0, six-month momentum.', 'Signal 8: RSI14 > 50, positive medium-term oscillator regime.', 'Risk-on when K=6 of 8 signals pass.', 'Hold QLD when ON and ZROZ otherwise.'],
    status: 'Strong in-sample; failed PBO/DSR validation.',
  },
  'Stage3 shared TQQQ': {
    concept: 'Same eight-signal Octa Price K6 vote with TQQQ risk-on.',
    algorithm: ['Use the identical 8-signal K=6 vote: price>SMA10, price>EMA200, price>SMA250, price>EMA250, ROC20>0, ROC60>0, ROC120>0, and RSI14>50.', 'Hold TQQQ when ON and ZROZ otherwise.', 'This increases convexity and terminal equity at the cost of deeper drawdowns.'],
    status: 'High CAGR; failed PBO/DSR validation.',
  },
  'Stage4-inside iter030 turbo': {
    concept: 'Hybrid inserting a five-signal trend/momentum/volatility vote as an extra QLD-to-TQQQ turbo gate inside Rearm T35D60.',
    algorithm: ['Keep the full Rearm T35D60 shell, LRS1.20 overlay and rate-vol defensive override.', 'Compute the Quint TrendMomVol K3 vote on QQQ: SMA100>SMA250, ROC10>0, ROC120>0, StochRSI14>50, and RV21 percentile<70.', 'Upgrade QLD to TQQQ when either canonical T35D60 rearm or the Quint TrendMomVol K3 vote says turbo is active.', 'Leave all other rearm mechanics unchanged.'],
    status: 'Raises CAGR/terminal equity but worsens MDD and Sortino, so it does not dominate Rearm T35D60.',
  },
  'Stage4 QLD base vote': {
    concept: 'Five-signal trend/momentum/volatility vote reproduced on testfolio with QLD risk-on. The name means it watches a quint of filters and turns ON when 3 of 5 pass.',
    algorithm: ['Build the 5-signal Quint TrendMomVol K3 vote on QQQ.', 'Signal 1: SMA100 > SMA250, medium trend above long trend.', 'Signal 2: ROC10 > 0, short momentum positive.', 'Signal 3: ROC120 > 0, six-month momentum positive.', 'Signal 4: StochRSI14 > 50, oscillator regime above midline.', 'Signal 5: RV21 percentile < 70 over a 1260-day rolling rank, avoiding high-volatility regimes.', 'Risk-on when K=3 of 5 signals pass.', 'Hold QLD when ON and ZROZ otherwise in this long-history reproduction.'],
    status: 'Strong in modern data, weaker over 1986+.',
  },
  'Stage4 TQQQ base vote': {
    concept: 'Same five-signal Quint TrendMomVol K3 vote with TQQQ risk-on.',
    algorithm: ['Use the same 5-signal K=3 vote: SMA100>SMA250, ROC10>0, ROC120>0, StochRSI14>50, and RV21 percentile<70.', 'Hold TQQQ when ON and ZROZ otherwise.', 'No Quad Risk K2 shell, no rearm logic, and no rate-vol CASHX override.'],
    status: 'Aggressive modern challenger; weak long-history risk.',
  },
  'LRS 200d SSO': { concept: 'Gayed-style SPY>SMA200 baseline using SSO.', algorithm: ['If SPY closes above SMA200, hold SSO next bar.', 'Otherwise hold CASHX.'], status: 'Simple 2x S&P trend baseline.' },
  'LRS 200d UPRO': { concept: 'Gayed-style SPY>SMA200 baseline using UPRO.', algorithm: ['If SPY closes above SMA200, hold UPRO next bar.', 'Otherwise hold CASHX.'], status: 'Simple 3x S&P trend baseline.' },
  'LRS 200d QLD': { concept: 'Nasdaq LRS baseline using QQQ>SMA200 and QLD.', algorithm: ['If QQQ closes above SMA200, hold QLD next bar.', 'Otherwise hold CASHX.'], status: 'Simple 2x Nasdaq trend baseline.' },
  'LRS 200d TQQQ': { concept: 'Nasdaq LRS baseline using QQQ>SMA200 and TQQQ.', algorithm: ['If QQQ closes above SMA200, hold TQQQ next bar.', 'Otherwise hold CASHX.'], status: 'Simple 3x Nasdaq trend baseline.' },
  'QQQ buy_hold': { concept: 'Long-history Nasdaq/QQQ proxy buy-and-hold.', algorithm: ['Buy QQQSIM and hold.'], status: 'Passive Nasdaq comparator.' },
  'SPY buy_hold': { concept: 'Long-history S&P 500 proxy buy-and-hold.', algorithm: ['Buy SPYSIM and hold.'], status: 'Passive broad-market comparator.' },
};

export function App() {
  const [meta, setMeta] = useState<StrategiesPayload | null>(null);
  const [report, setReport] = useState<ReportPayload | null>(null);
  const [tab, setTab] = useState<'overview' | 'strategies'>('overview');
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const [a, setA] = useState('');
  const [b, setB] = useState('');
  const [visible, setVisible] = useState<Set<string>>(new Set());
  const [cursorIdx, setCursorIdx] = useState<number | null>(null);
  const [sortLegendByCursorEquity, setSortLegendByCursorEquity] = useState(false);
  const [sort, setSort] = useState<{ key: keyof MetricRow; dir: 1 | -1 }>({ key: 'sortino', dir: -1 });
  const [rangeOpen, setRangeOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchJson<StrategiesPayload>('/api/strategies').then((payload) => {
      setMeta(payload); setStart(payload.start); setEnd(payload.end); setA(payload.default_a); setB(payload.default_b);
      setVisible(new Set(payload.strategies));
      setError(null);
    }).catch((err: unknown) => setError(String(err instanceof Error ? err.message : err)));
  }, []);

  useEffect(() => { if (meta && start && end && a && b) void updateAll(); }, [meta]);

  const alias = (name: string) => meta?.aliases[name] ?? name;

  async function updateAll() {
    const qs = new URLSearchParams({ start, end, a, b });
    const payload = await fetchJson<ReportPayload>(`/api/report?${qs}`);
    setReport(payload);
    setCursorIdx(payload.series.dates.length - 1);
    setError(null);
  }

  const names = useMemo(() => report ? Object.keys(report.series.equity) : [], [report]);

  return <main>
    <h1>LETF Rotation Research Console</h1>
    <p>Compare rearm variants, Quad Risk K2, Octa Price K6, Quint TrendMomVol K3 and LRS baselines across equity, drawdown and rolling A/B windows. Research-only: DSR/PBO failures still block promotion.</p>
    {error && <div className="error-box">API error: {error}. Check if the Python backend is running on <code>127.0.0.1:8765</code>.</div>}
    <nav className="tabs">
      <button className={tab === 'overview' ? 'tab active' : 'tab'} onClick={() => setTab('overview')}>Overview</button>
      <button className={tab === 'strategies' ? 'tab active' : 'tab'} onClick={() => setTab('strategies')}>Strategies</button>
    </nav>
    {tab === 'overview' && <section>
      <div className="controls">
        {meta && <DateRangeControl start={start} end={end} min={meta.start} max={meta.end} open={rangeOpen} setOpen={setRangeOpen} setStart={setStart} setEnd={setEnd} />}
        <button onClick={() => void updateAll().catch((err: unknown) => setError(String(err instanceof Error ? err.message : err)))}>Update all</button>
      </div>
      {report && <>
        <WindowSummary report={report} alias={alias} />
        <section className="panel"><h2>Equity Curves</h2><ChartSection report={report} names={names} alias={alias} visible={visible} setVisible={setVisible} cursorIdx={cursorIdx} setCursorIdx={setCursorIdx} sortLegendByCursorEquity={sortLegendByCursorEquity} setSortLegendByCursorEquity={setSortLegendByCursorEquity} /></section>
        <section className="panel"><RollingABComparison report={report} names={names} a={a} b={b} setA={setA} setB={setB} alias={alias} /></section>
        <section className="panel"><h2>Metrics</h2><Metrics rows={report.metrics} alias={alias} sort={sort} setSort={setSort} /></section>
      </>}
    </section>}
    {tab === 'strategies' && <section className="panel"><h2>Strategy Concepts</h2>{meta?.strategies.map(name => <StrategyDoc key={name} name={name} alias={alias} />)}</section>}
  </main>;
}

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  const text = await response.text();
  if (!response.ok) {
    throw new Error(text || `${response.status} ${response.statusText}`);
  }
  if (!text) {
    throw new Error('empty response from API');
  }
  const payload = JSON.parse(text) as T & { error?: string };
  if (payload.error) {
    throw new Error(payload.error);
  }
  return payload as T;
}

function DateRangeControl({ start, end, min, max, open, setOpen, setStart, setEnd }: { start: string; end: string; min: string; max: string; open: boolean; setOpen: (v: boolean) => void; setStart: (v: string) => void; setEnd: (v: string) => void }) {
  const selected = useMemo<DateRange>(() => ({ from: parseDate(start), to: parseDate(end) }), [start, end]);
  const presets = [
    ['Full', min, max],
    ['20y', shiftYear(max, -20), max],
    ['15y', shiftYear(max, -15), max],
    ['10y', shiftYear(max, -10), max],
    ['5y', shiftYear(max, -5), max],
  ];
  function onSelect(range: DateRange | undefined) {
    if (range?.from) setStart(formatDateInput(range.from));
    if (range?.to) setEnd(formatDateInput(range.to));
  }
  return <div className="date-range-control"><span className="range-label">Date range</span><button type="button" className="date-range-button" onClick={() => setOpen(!open)}><strong>{start}</strong><span>→</span><strong>{end}</strong></button>{open && <div className="date-range-popover"><div className="range-presets">{presets.map(([label, s, e]) => <button key={label} type="button" onClick={() => { setStart(maxDate(s, min)); setEnd(e); setOpen(false); }}>{label}</button>)}</div><DayPicker mode="range" selected={selected} onSelect={onSelect} numberOfMonths={2} captionLayout="dropdown" startMonth={parseDate(min)} endMonth={parseDate(max)} disabled={{ before: parseDate(min), after: parseDate(max) }} /></div>}</div>;
}

function parseDate(value: string) { const [y, m, d] = value.split('-').map(Number); return new Date(y, m - 1, d); }
function formatDateInput(date: Date) { return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`; }
function shiftYear(value: string, years: number) { const d = parseDate(value); d.setFullYear(d.getFullYear() + years); return formatDateInput(d); }
function maxDate(a: string, b: string) { return a > b ? a : b; }

function WindowSummary({ report, alias }: { report: ReportPayload; alias: (name: string) => string }) {
  const bestCagr = [...report.metrics].sort((x, y) => y.cagr - x.cagr)[0];
  const bestSortino = [...report.metrics].sort((x, y) => y.sortino - x.sortino)[0];
  const lowMdd = [...report.metrics].sort((x, y) => y.mdd - x.mdd)[0];
  const cards = [['Start', report.start], ['End', report.end], ['Bars', fmtNum(report.n_days)], ['Best CAGR', `${alias(bestCagr.label)} ${fmtPct(bestCagr.cagr)}`], ['Best Sortino', `${alias(bestSortino.label)} ${bestSortino.sortino.toFixed(3)}`], ['Lowest MDD', `${alias(lowMdd.label)} ${fmtPct(lowMdd.mdd)}`]];
  return <section className="panel"><h2>Window Summary</h2><div className="summary">{cards.map(([k, v]) => <div className="card" key={k}><small>{k}</small><strong>{v}</strong></div>)}</div></section>;
}

function ChartSection(props: { report: ReportPayload; names: string[]; alias: (name: string) => string; visible: Set<string>; setVisible: (v: Set<string>) => void; cursorIdx: number | null; setCursorIdx: (v: number | null) => void; sortLegendByCursorEquity: boolean; setSortLegendByCursorEquity: (v: boolean) => void }) {
  const { report, names, alias, visible, setVisible, cursorIdx, setCursorIdx, sortLegendByCursorEquity, setSortLegendByCursorEquity } = props;
  return <div className="plot-layout"><div className="plot-stack" onMouseLeave={() => setCursorIdx(null)}><UPlotChart report={report} names={names} alias={alias} visible={visible} kind="equity" onCursor={setCursorIdx} /><div><h2>Drawdown</h2><UPlotChart report={report} names={names} alias={alias} visible={visible} kind="drawdown" onCursor={setCursorIdx} /></div></div><SeriesTable report={report} names={names} alias={alias} visible={visible} setVisible={setVisible} cursorIdx={cursorIdx} sortByCursorEquity={sortLegendByCursorEquity} setSortByCursorEquity={setSortLegendByCursorEquity} /></div>;
}

function UPlotChart({ report, names, alias, visible, kind, onCursor }: { report: ReportPayload; names: string[]; alias: (name: string) => string; visible: Set<string>; kind: 'equity' | 'drawdown'; onCursor: (v: number) => void }) {
  const ref = useRef<HTMLDivElement | null>(null);
  const plot = useRef<uPlot | null>(null);
  useEffect(() => {
    if (!ref.current) return;
    const x = report.series.dates.map(d => new Date(`${d}T00:00:00Z`).getTime() / 1000);
    const data = [x, ...names.map(n => kind === 'equity' ? report.series.equity[n] : report.series.drawdown[n].map(v => v * 100))];
    const opts: uPlot.Options = { width: ref.current.clientWidth || 900, height: 358, legend: { show: false }, cursor: { sync: { key: 'td-report' } }, scales: { x: { time: true }, y: kind === 'equity' ? { distr: 3, log: 10 } : {} }, axes: [{ stroke: '#6b7280', grid: { stroke: '#edf0f5' } }, { stroke: '#6b7280', grid: { stroke: '#edf0f5' } }], series: [{}, ...names.map((n, i) => ({ label: alias(n), stroke: palette[i % palette.length], width: 1.6, points: { show: false }, show: visible.has(n) }))], hooks: { setCursor: [u => { if (u.cursor.idx != null) onCursor(u.cursor.idx); }] } };
    plot.current?.destroy(); plot.current = new uPlot(opts, data as uPlot.AlignedData, ref.current);
    return () => plot.current?.destroy();
  }, [report, names, kind]);
  useEffect(() => { names.forEach((n, i) => plot.current?.setSeries(i + 1, { show: visible.has(n) })); }, [visible, names]);
  return <div ref={ref} className="plot" />;
}

function SeriesTable({ report, names, alias, visible, setVisible, cursorIdx, sortByCursorEquity, setSortByCursorEquity }: { report: ReportPayload; names: string[]; alias: (name: string) => string; visible: Set<string>; setVisible: (v: Set<string>) => void; cursorIdx: number | null; sortByCursorEquity: boolean; setSortByCursorEquity: (v: boolean) => void }) {
  const hasCursor = cursorIdx != null;
  const idx = hasCursor ? Math.max(0, Math.min(report.series.dates.length - 1, cursorIdx)) : report.series.dates.length - 1;
  const metricsByName = new Map(report.metrics.map(row => [row.label, row]));
  const colorByName = new Map(names.map((name, i) => [name, palette[i % palette.length]]));
  const sortedNames = [...names].sort((x, y) => sortByCursorEquity ? report.series.equity[y][idx] - report.series.equity[x][idx] : (metricsByName.get(y)?.sortino ?? -Infinity) - (metricsByName.get(x)?.sortino ?? -Infinity));
  return <aside className="legend-panel"><table><thead><tr><th className="legend-date-label">Date</th><th className="legend-date-value">{hasCursor ? report.series.dates[idx] : report.end}</th><th colSpan={2}><label className="legend-sort-toggle"><input type="checkbox" checked={sortByCursorEquity} onChange={e => setSortByCursorEquity(e.target.checked)} />Sort by cursor equity</label></th></tr><tr><th>Color</th><th>Name</th><th>Equity</th><th>{hasCursor ? 'Drawdown' : 'Max Drawdown'}</th></tr></thead><tbody>{sortedNames.map((n) => {
    const metric = metricsByName.get(n);
    return <tr key={n} className={visible.has(n) ? '' : 'off'} onClick={() => { const next = new Set(visible); next.has(n) ? next.delete(n) : next.add(n); setVisible(next); }}><td><span className="color-chip" style={{ background: colorByName.get(n) }} /></td><td title={n}><span className="series-name"><strong>{alias(n)}</strong>{metric && <small>CAGR {fmtPct(metric.cagr)} · MaxDD {fmtPct(metric.mdd)}</small>}</span></td><td>{fmtMult(report.series.equity[n][idx])}</td><td>{fmtPct(hasCursor ? report.series.drawdown[n][idx] : metric?.mdd ?? Math.min(...report.series.drawdown[n]))}</td></tr>;
  })}</tbody></table></aside>;
}

function RollingABComparison({ report, names, a, b, setA, setB, alias }: { report: ReportPayload; names: string[]; a: string; b: string; setA: (v: string) => void; setB: (v: string) => void; alias: (name: string) => string }) {
  const data = useMemo(() => computeHeatmap(report, a, b), [report, a, b]);
  const [hover, setHover] = useState<HeatHover>(null);
  const [focusWindow, setFocusWindow] = useState(5);
  return <div className="ab-panel"><div className="ab-header"><div><h2>Rolling A/B Comparison</h2><p>Month-end rolling windows · 3, 5, 10, 15, 20 years</p></div><button className="ab-swap" onClick={() => { setA(b); setB(a); setHover(null); }}>↔ Swap</button></div><div className="ab-pickers"><label>A · Primary<select value={a} onChange={e => { setA(e.target.value); setHover(null); }}>{names.filter(n => n !== b).map(n => <option key={n} value={n}>{alias(n)}</option>)}</select></label><label>B · Benchmark<select value={b} onChange={e => { setB(e.target.value); setHover(null); }}>{names.filter(n => n !== a).map(n => <option key={n} value={n}>{alias(n)}</option>)}</select></label></div><ABKpis report={report} a={a} b={b} alias={alias} /><div className="ab-layout"><div className="ab-main"><CanvasHeatmap title="Win Rate" subtitle="% of days A above B inside each rolling window" data={data.pct} dates={data.x} rows={data.y} hover={hover} setHover={setHover} percent /><CanvasHeatmap title="Final Ratio" subtitle="A growth ÷ B growth at window close" data={data.ratio} dates={data.x} rows={data.y} hover={hover} setHover={setHover} /></div><aside className="ab-sidebar"><ABHoverDetail report={report} a={a} b={b} alias={alias} data={data} hover={hover} /><ABDistribution data={data} hover={hover} focusWindow={focusWindow} setFocusWindow={setFocusWindow} /></aside></div><div className="note">{alias(a)} / {alias(b)}. Heatmaps are computed in the browser from cached daily equity.</div></div>;
}

function ABKpis({ report, a, b, alias }: { report: ReportPayload; a: string; b: string; alias: (name: string) => string }) {
  const eq = report.series.equity; const dd = report.series.drawdown;
  const rel = eq[a].map((v, i) => v / eq[b][i]);
  const cards = [[`A · ${alias(a)}`, fmtMult(eq[a].at(-1) ?? 0), 'end equity'], [`B · ${alias(b)}`, fmtMult(eq[b].at(-1) ?? 0), 'end equity'], ['A/B final', fmtNum(rel.at(-1) ?? 0), rel.at(-1)! >= 1 ? 'A leads' : 'B leads'], ['Days A > B', fmtPct(rel.filter(v => v > 1).length / rel.length), 'over full series'], ['A max DD', fmtPct(Math.min(...dd[a])), 'peak-to-trough'], ['B max DD', fmtPct(Math.min(...dd[b])), 'peak-to-trough']];
  return <div className="ab-kpis">{cards.map(([k, v, s]) => <div className="ab-kpi" key={k}><small>{k}</small><strong>{v}</strong><span>{s}</span></div>)}</div>;
}

function computeHeatmap(report: ReportPayload, a: string, b: string) {
  const dates = report.series.dates; const rel = report.series.equity[a].map((v, i) => v / report.series.equity[b][i]);
  const monthEnds: number[] = []; for (let i = 0; i < dates.length; i++) if (dates[i].slice(0, 7) !== dates[i + 1]?.slice(0, 7)) monthEnds.push(i);
  const validEnds = monthEnds.filter(i => i >= 3 * 252); const x = validEnds.map(i => dates[i]);
  const pct: (number | null)[][] = []; const ratio: (number | null)[][] = [];
  const startIdx: (number | null)[][] = []; const endIdx: number[][] = [];
  for (const years of windows) {
    const n = years * 252; const pr: (number | null)[] = []; const rr: (number | null)[] = [];
    const sr: (number | null)[] = []; const er: number[] = [];
    for (const idx of validEnds) {
      er.push(idx);
      if (idx < n) { pr.push(null); rr.push(null); sr.push(null); continue; }
      const start = idx - n + 1; const slice = rel.slice(start, idx + 1);
      pr.push(slice.filter(v => v > 1).length / slice.length); rr.push(rel[idx] / rel[start]);
      sr.push(start);
    }
    pct.push(pr); ratio.push(rr); startIdx.push(sr); endIdx.push(er);
  }
  return { x, y: windows.map(w => `${w}y`), pct, ratio, startIdx, endIdx };
}

function CanvasHeatmap({ title, subtitle, data, dates, rows, hover, setHover, percent = false }: { title: string; subtitle: string; data: (number | null)[][]; dates: string[]; rows: string[]; hover: HeatHover; setHover: (v: HeatHover) => void; percent?: boolean }) {
  const canvas = useRef<HTMLCanvasElement | null>(null);
  useEffect(() => {
    const c = canvas.current; if (!c) return; const ctx = c.getContext('2d')!; const w = c.clientWidth, h = c.clientHeight; c.width = w * devicePixelRatio; c.height = h * devicePixelRatio; ctx.scale(devicePixelRatio, devicePixelRatio); ctx.clearRect(0, 0, w, h);
    const left = 44, top = 22, cw = (w - left - 8) / Math.max(1, dates.length), ch = (h - top - 22) / rows.length;
    ctx.font = '12px IBM Plex Sans'; ctx.fillStyle = '#6b7280'; rows.forEach((r, i) => ctx.fillText(r, 8, top + i * ch + ch * 0.62));
    data.forEach((row, y) => row.forEach((v, x) => { if (v == null) return; ctx.fillStyle = percent ? colorPct(v) : colorRatio(v); ctx.fillRect(left + x * cw, top + y * ch, Math.max(1, cw), Math.max(1, ch)); }));
    if (hover) { const hx = left + hover.x * cw + cw / 2; ctx.fillStyle = 'rgba(28, 39, 60, 0.85)'; ctx.fillRect(hx, top, 1, h - top - 22); }
  }, [data, dates, rows, percent, hover]);
  function onMove(e: MouseEvent<HTMLCanvasElement>) { const rect = e.currentTarget.getBoundingClientRect(); const left = 44, top = 22, cw = (rect.width - left - 8) / Math.max(1, dates.length), ch = (rect.height - top - 22) / rows.length; const x = Math.floor((e.clientX - rect.left - left) / cw); const y = Math.floor((e.clientY - rect.top - top) / ch); const v = data[y]?.[x]; setHover(v == null ? null : { x, y }); }
  return <div className="heatmap-card"><div className="heatmap-title"><h3>{title}</h3><span>{subtitle}</span></div><canvas ref={canvas} className="canvas-heatmap" onMouseMove={onMove} onMouseLeave={() => setHover(null)} /></div>;
}

function ABHoverDetail({ report, a, b, alias, data, hover }: { report: ReportPayload; a: string; b: string; alias: (name: string) => string; data: ReturnType<typeof computeHeatmap>; hover: HeatHover }) {
  if (!hover) return <div className="ab-detail"><small>Window</small><strong>Hover a heatmap cell</strong><span>Range, win rate and final ratio appear here.</span></div>;
  const start = data.startIdx[hover.y]?.[hover.x]; const end = data.endIdx[hover.y]?.[hover.x];
  if (start == null || end == null) return <div className="ab-detail"><small>Window</small><strong>Out of range</strong><span>This window needs more history.</span></div>;
  const years = windows[hover.y]; const eqA = report.series.equity[a]; const eqB = report.series.equity[b];
  const growthA = eqA[end] / eqA[start]; const growthB = eqB[end] / eqB[start]; const ratio = growthA / growthB;
  const cagrA = Math.pow(growthA, 1 / years) - 1; const cagrB = Math.pow(growthB, 1 / years) - 1; const winRate = data.pct[hover.y][hover.x] ?? 0;
  return <div className="ab-detail"><small>Window · {data.y[hover.y]}</small><strong>{report.series.dates[start]} → {report.series.dates[end]}</strong><span>{fmtNum(end - start + 1)} trading days · {years}.0 years</span><div className="ab-detail-pair"><div><small>A · {alias(a)}</small><strong>{fmtMult(growthA)}</strong><span>{fmtPct(cagrA)} CAGR</span></div><div><small>B · {alias(b)}</small><strong>{fmtMult(growthB)}</strong><span>{fmtPct(cagrB)} CAGR</span></div></div><div className={ratio >= 1 ? 'ab-verdict a-win' : 'ab-verdict b-win'}><small>Verdict</small><strong>{ratio >= 1 ? `A · ${fmtNum(ratio)}x B` : `B · ${fmtNum(1 / ratio)}x A`}</strong><span>{fmtPct(winRate)} of days · A above B</span></div></div>;
}

function ABDistribution({ data, hover, focusWindow, setFocusWindow }: { data: ReturnType<typeof computeHeatmap>; hover: HeatHover; focusWindow: number; setFocusWindow: (v: number) => void }) {
  const available = windows.map((_, i) => data.ratio[i].some(v => v != null));
  let rowIdx = windows.indexOf(focusWindow);
  if (rowIdx < 0 || !available[rowIdx]) rowIdx = Math.max(0, available.findIndex(Boolean));
  const effectiveWindow = windows[rowIdx];
  const samples = data.ratio[rowIdx].filter((v): v is number => v != null).sort((x, y) => x - y);
  if (!samples.length) return <div className="ab-distribution"><div className="ab-window-pills">{windows.map(w => <button key={w} disabled>{w}y</button>)}</div><div className="note">Selected date range is too short for rolling-window distribution.</div></div>;
  const bins = 18; const lo = Math.max(0.01, samples[0]); const hi = samples.at(-1) ?? 1; const logLo = Math.log(lo), logHi = Math.log(Math.max(hi, lo * 1.01));
  const counts = new Array(bins).fill(0);
  samples.forEach(v => { const t = (Math.log(v) - logLo) / (logHi - logLo); const idx = Math.max(0, Math.min(bins - 1, Math.floor(t * bins))); counts[idx] += 1; });
  const maxCount = Math.max(...counts, 1); const hoverVal = hover && data.ratio[rowIdx][hover.x] != null ? data.ratio[rowIdx][hover.x] : null;
  const p = (q: number) => samples[Math.min(samples.length - 1, Math.floor(samples.length * q))];
  const hoverLeft = hoverVal == null ? null : `${(((Math.log(hoverVal) - logLo) / (logHi - logLo)) * 100).toFixed(2)}%`;
  return <div className="ab-distribution"><div className="ab-window-pills">{windows.map((w, i) => <button key={w} className={w === effectiveWindow ? 'active' : ''} disabled={!available[i]} onClick={() => available[i] && setFocusWindow(w)}>{w}y</button>)}</div><div className="ab-dist-head"><small>Distribution · {effectiveWindow}y final ratio</small><span>{samples.length} samples</span></div><div className="ab-histogram">{counts.map((c, i) => <span key={i} style={{ height: `${Math.max(3, (c / maxCount) * 86)}px`, background: colorRatio(Math.exp(logLo + ((i + 0.5) / bins) * (logHi - logLo))) }} />)}{hoverLeft && <i style={{ left: hoverLeft }} />}</div><div className="ab-dist-stats"><small>p10</small><small>median</small><small>p90</small><strong>{fmtMult(p(0.1))}</strong><strong>{fmtMult(p(0.5))}</strong><strong>{fmtMult(p(0.9))}</strong></div></div>;
}

function Metrics({ rows, alias, sort, setSort }: { rows: MetricRow[]; alias: (name: string) => string; sort: { key: keyof MetricRow; dir: 1 | -1 }; setSort: (v: { key: keyof MetricRow; dir: 1 | -1 }) => void }) {
  const sorted = [...rows].sort((a, b) => ((a[sort.key] as string | number) > (b[sort.key] as string | number) ? 1 : -1) * sort.dir);
  const cols: [keyof MetricRow, string][] = [['label', 'Strategy'], ['cagr', 'CAGR'], ['sortino', 'Sortino'], ['sharpe', 'Sharpe'], ['mdd', 'MDD'], ['calmar', 'Calmar'], ['end_mult', 'End']];
  return <table className="metrics-table"><thead><tr>{cols.map(([k, label]) => <th key={k} onClick={() => setSort(sort.key === k ? { key: k, dir: (sort.dir * -1) as 1 | -1 } : { key: k, dir: k === 'label' ? 1 : -1 })}>{label}{sort.key === k ? (sort.dir > 0 ? ' ▲' : ' ▼') : ''}</th>)}</tr></thead><tbody>{sorted.map(r => <tr key={r.label}><td title={r.label}>{alias(r.label)}</td><td>{fmtPct(r.cagr)}</td><td>{r.sortino.toFixed(3)}</td><td>{r.sharpe.toFixed(3)}</td><td>{fmtPct(r.mdd)}</td><td>{r.calmar.toFixed(3)}</td><td>{fmtMult(r.end_mult)}</td></tr>)}</tbody></table>;
}

function StrategyDoc({ name, alias }: { name: string; alias: (name: string) => string }) { const d = docs[name]; return <details open><summary>{alias(name)}</summary><div className="strategy-body"><p><strong>Concept:</strong> {d?.concept ?? 'No description available.'}</p><div><strong className="strategy-section-label">Algorithm:</strong><ul>{(d?.algorithm ?? []).map(x => <li key={x}>{x}</li>)}</ul></div><p><strong>Status:</strong> {d?.status}</p></div></details>; }

function colorPct(v: number) { const t = Math.max(0, Math.min(1, v)); return mixColor(t); }
function colorRatio(v: number) { const t = Math.max(0, Math.min(1, (Math.log(v) + 1.5) / 3)); return mixColor(t); }
function mixColor(t: number) { const red = [215, 48, 39], white = [247, 247, 247], blue = [33, 102, 172]; const a = t < 0.5 ? red : white; const b = t < 0.5 ? white : blue; const u = t < 0.5 ? t * 2 : (t - 0.5) * 2; return `rgb(${a.map((x, i) => Math.round(x + (b[i] - x) * u)).join(',')})`; }
function fmtPct(x: number) { return `${(x * 100).toFixed(2)}%`; }
function fmtNum(x: number) { return x.toLocaleString(undefined, { maximumFractionDigits: 2 }); }
function fmtMult(x: number) { return `${fmtNum(x)}x`; }
