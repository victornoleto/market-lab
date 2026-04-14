-- ai-trade — initial Postgres schema.
-- Loaded once on container init via /docker-entrypoint-initdb.d/01_init.sql.
-- Subsequent changes go through migration files (scheme TBD; SQL-only for now).
--
-- Schemas (see ROADMAP.md §Fase 1):
--   market_data    — OHLCV cache (trendbars) + ticks stream
--   trades         — order lifecycle + position lifecycle
--   features       — per-symbol feature snapshots for strategies
--   logs           — structured app log
--   backtest_runs  — one row per backtest execution with metrics

CREATE SCHEMA IF NOT EXISTS market_data;
CREATE SCHEMA IF NOT EXISTS trades;
CREATE SCHEMA IF NOT EXISTS features;
CREATE SCHEMA IF NOT EXISTS logs;
CREATE SCHEMA IF NOT EXISTS backtest_runs;

-- -----------------------------------------------------------------------------
-- market_data
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS market_data.trendbars (
    symbol_id     BIGINT           NOT NULL,
    symbol_name   TEXT             NOT NULL,
    period        TEXT             NOT NULL,  -- M1, M5, H1, D1, ...
    ts            TIMESTAMPTZ      NOT NULL,
    open          DOUBLE PRECISION NOT NULL,
    high          DOUBLE PRECISION NOT NULL,
    low           DOUBLE PRECISION NOT NULL,
    close         DOUBLE PRECISION NOT NULL,
    volume        BIGINT           NOT NULL,
    ingested_at   TIMESTAMPTZ      NOT NULL DEFAULT now(),
    PRIMARY KEY (symbol_id, period, ts)
);

CREATE INDEX IF NOT EXISTS trendbars_name_period_ts
    ON market_data.trendbars (symbol_name, period, ts DESC);

CREATE TABLE IF NOT EXISTS market_data.ticks (
    symbol_id     BIGINT           NOT NULL,
    symbol_name   TEXT             NOT NULL,
    ts            TIMESTAMPTZ      NOT NULL,
    bid           DOUBLE PRECISION,
    ask           DOUBLE PRECISION,
    ingested_at   TIMESTAMPTZ      NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ticks_name_ts
    ON market_data.ticks (symbol_name, ts DESC);

-- Symbols discovered via ProtoOASymbolsListReq. Cache the full list so we can
-- filter by liquidity/spread offline and pick the active universe (Fase 2.0).
CREATE TABLE IF NOT EXISTS market_data.symbols (
    symbol_id       BIGINT PRIMARY KEY,
    symbol_name     TEXT NOT NULL UNIQUE,
    asset_class     TEXT,
    description     TEXT,
    digits          INT,
    pip_position    INT,
    enabled         BOOLEAN NOT NULL DEFAULT TRUE,
    refreshed_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- -----------------------------------------------------------------------------
-- trades
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS trades.orders (
    id                BIGSERIAL PRIMARY KEY,
    client_order_id   TEXT UNIQUE,
    ctrader_order_id  BIGINT,
    symbol_id         BIGINT NOT NULL,
    symbol_name       TEXT   NOT NULL,
    side              TEXT   NOT NULL CHECK (side IN ('BUY', 'SELL')),
    order_type        TEXT   NOT NULL CHECK (order_type IN ('MARKET', 'LIMIT', 'STOP', 'STOP_LIMIT')),
    requested_volume  BIGINT NOT NULL,
    filled_volume     BIGINT NOT NULL DEFAULT 0,
    limit_price       DOUBLE PRECISION,
    stop_price        DOUBLE PRECISION,
    status            TEXT   NOT NULL,  -- PENDING, ACCEPTED, PARTIAL, FILLED, CANCELLED, REJECTED
    strategy_id       TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS trades.positions (
    id                BIGSERIAL PRIMARY KEY,
    ctrader_position_id BIGINT UNIQUE,
    symbol_id         BIGINT NOT NULL,
    symbol_name       TEXT   NOT NULL,
    side              TEXT   NOT NULL CHECK (side IN ('BUY', 'SELL')),
    volume            BIGINT NOT NULL,
    avg_entry_price   DOUBLE PRECISION,
    stop_loss         DOUBLE PRECISION,
    take_profit       DOUBLE PRECISION,
    status            TEXT   NOT NULL CHECK (status IN ('OPEN', 'CLOSED')),
    strategy_id       TEXT,
    opened_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    closed_at         TIMESTAMPTZ,
    realized_pnl      DOUBLE PRECISION
);

-- -----------------------------------------------------------------------------
-- features
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS features.snapshots (
    symbol_name   TEXT        NOT NULL,
    ts            TIMESTAMPTZ NOT NULL,
    feature_set   TEXT        NOT NULL,  -- e.g. "clenow_momentum_v1"
    payload       JSONB       NOT NULL,
    PRIMARY KEY (symbol_name, feature_set, ts)
);

-- -----------------------------------------------------------------------------
-- logs
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS logs.events (
    id         BIGSERIAL PRIMARY KEY,
    ts         TIMESTAMPTZ NOT NULL DEFAULT now(),
    level      TEXT        NOT NULL,      -- DEBUG, INFO, WARN, ERROR
    component  TEXT        NOT NULL,      -- e.g. "ctrader.client", "strategy.momentum"
    event      TEXT        NOT NULL,
    context    JSONB
);

CREATE INDEX IF NOT EXISTS events_ts_level
    ON logs.events (ts DESC, level);

-- -----------------------------------------------------------------------------
-- backtest_runs
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS backtest_runs.runs (
    id            BIGSERIAL PRIMARY KEY,
    strategy_id   TEXT        NOT NULL,
    params        JSONB       NOT NULL,
    universe      TEXT[]      NOT NULL,
    start_ts      TIMESTAMPTZ NOT NULL,
    end_ts        TIMESTAMPTZ NOT NULL,
    started_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at   TIMESTAMPTZ,
    metrics       JSONB,   -- Sharpe, DSR, PBO, max DD, etc.
    git_sha       TEXT
);
