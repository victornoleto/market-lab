import type {
  ContributionRow,
  CurrentPortfolio,
  HistoryEvent,
  Meta,
  Methodologies,
  SeriesPoint,
  StrategyIndex,
} from "./types";

const BASE = "/api";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(BASE + path);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} — ${path}`);
  return res.json() as Promise<T>;
}

const q = (universe: string, window?: string) =>
  `?universe=${encodeURIComponent(universe)}` + (window ? `&window=${encodeURIComponent(window)}` : "");
const n = (name: string) => encodeURIComponent(name);

export const api = {
  windows: (u: string) => get<{ universe: string; windows: string[] }>(`/windows?universe=${u}`),
  strategies: (u: string, w?: string) => get<StrategyIndex>(`/strategies${q(u, w)}`),
  meta: (name: string, u: string, w?: string) => get<Meta>(`/strategies/${n(name)}${q(u, w)}`),
  current: (name: string, u: string, w?: string) =>
    get<CurrentPortfolio>(`/strategies/${n(name)}/portfolio/current${q(u, w)}`),
  history: (name: string, u: string, w?: string) =>
    get<HistoryEvent[]>(`/strategies/${n(name)}/portfolio/history${q(u, w)}`),
  contribution: (name: string, u: string, w?: string) =>
    get<ContributionRow[]>(`/strategies/${n(name)}/contribution${q(u, w)}`),
  series: (name: string, u: string, w?: string) =>
    get<SeriesPoint[]>(`/strategies/${n(name)}/series${q(u, w)}`),
  methodologies: () => get<Methodologies>(`/methodologies`),
};
