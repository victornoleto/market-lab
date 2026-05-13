export type MetricRow = {
  label: string;
  cagr: number;
  sortino: number;
  sharpe: number;
  mdd: number;
  calmar: number;
  end_mult: number;
};

export type StrategiesPayload = {
  start: string;
  end: string;
  strategies: string[];
  aliases: Record<string, string>;
  default_a: string;
  default_b: string;
  window_years: number[];
};

export type ReportPayload = {
  start: string;
  end: string;
  n_days: number;
  strategy_a: string;
  strategy_b: string;
  metrics: MetricRow[];
  summary: {
    a_end_equity: number;
    b_end_equity: number;
    a_over_b_end: number;
    pct_days_a_above_b: number;
    a_mdd: number;
    b_mdd: number;
  };
  series: {
    dates: string[];
    equity: Record<string, number[]>;
    drawdown: Record<string, number[]>;
  };
};
