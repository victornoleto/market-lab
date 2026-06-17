export interface IndexEntry {
  name: string;
  mechanism: string;
  top_n: number;
  rebalance_months: number;
  as_of: string | null;
  cagr: number;
  mdd: number;
  sharpe: number;
  gate_pass: boolean;
  kind?: string;
}

export interface StrategyIndex {
  universe: string;
  window: string;
  benchmark: string;
  strategies: IndexEntry[];
  disclaimer: string;
}

export interface Holding {
  ticker: string;
  weight: number;
}

export interface CurrentPortfolio {
  as_of: string | null;
  holdings: Holding[];
}

export interface HistoryEvent {
  date: string;
  holdings: Holding[];
  entered: string[];
  exited: string[];
}

export interface ContributionRow {
  ticker: string;
  contribution: number;
  last_weight: number;
}

export type SeriesPoint = { date: string } & Record<string, number | string | null>;

export interface Meta {
  name: string;
  mechanism: string;
  score_mode?: string;
  lookback?: string;
  top_n: number;
  rebalance_months: number;
  weight_mode: string;
  absolute_filter?: boolean;
  metrics: Record<string, number | null>;
  gate_verdict: Record<string, unknown> | null;
  promotion_eligible: boolean;
  disclaimer: string;
  as_of: string | null;
  n_rebalances?: number;
}

export interface Methodologies {
  disclaimer: string;
  score_modes: Record<string, string>;
  scoring: string;
  weighting: string;
  rebalance: string;
  gates: Record<string, unknown>;
}
