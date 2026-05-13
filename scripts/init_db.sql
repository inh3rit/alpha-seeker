-- Alpha Seeker 数据库建表脚本
-- PostgreSQL 15+
-- 使用方式：
--   psql -U alpha_seeker -d alpha_seeker -f scripts/init_db.sql
--   或
--   docker exec -i alpha-seeker-postgres psql -U alpha_seeker -d alpha_seeker < scripts/init_db.sql

-- ============================================================
-- 股票基本信息表
-- ============================================================
CREATE TABLE IF NOT EXISTS stocks (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    industry VARCHAR(50),
    sector VARCHAR(50),
    list_date DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE stocks IS '股票基本信息';
COMMENT ON COLUMN stocks.code IS '股票代码（如 600519）';
COMMENT ON COLUMN stocks.name IS '股票名称';
COMMENT ON COLUMN stocks.industry IS '所属行业';
COMMENT ON COLUMN stocks.sector IS '板块（主板/创业板/科创板）';
COMMENT ON COLUMN stocks.list_date IS '上市日期';


-- ============================================================
-- 日线行情数据表
-- ============================================================
CREATE TABLE IF NOT EXISTS daily_quotes (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    open NUMERIC(10, 2) NOT NULL,
    close NUMERIC(10, 2) NOT NULL,
    high NUMERIC(10, 2) NOT NULL,
    low NUMERIC(10, 2) NOT NULL,
    volume BIGINT NOT NULL,
    amount NUMERIC(20, 2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_daily_quotes_code_date UNIQUE (code, trade_date)
);

CREATE INDEX IF NOT EXISTS ix_daily_quotes_code ON daily_quotes(code);
CREATE INDEX IF NOT EXISTS ix_daily_quotes_trade_date ON daily_quotes(trade_date);
CREATE INDEX IF NOT EXISTS ix_daily_quotes_code_date ON daily_quotes(code, trade_date);

COMMENT ON TABLE daily_quotes IS '日线行情（前复权）';
COMMENT ON COLUMN daily_quotes.open IS '开盘价';
COMMENT ON COLUMN daily_quotes.close IS '收盘价';
COMMENT ON COLUMN daily_quotes.high IS '最高价';
COMMENT ON COLUMN daily_quotes.low IS '最低价';
COMMENT ON COLUMN daily_quotes.volume IS '成交量（手）';
COMMENT ON COLUMN daily_quotes.amount IS '成交额（元）';


-- ============================================================
-- 技术指标缓存表
-- ============================================================
CREATE TABLE IF NOT EXISTS indicators (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    indicator_type VARCHAR(20) NOT NULL,
    indicator_value JSONB NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_indicators_code_date_type UNIQUE (code, trade_date, indicator_type)
);

CREATE INDEX IF NOT EXISTS ix_indicators_code ON indicators(code);
CREATE INDEX IF NOT EXISTS ix_indicators_trade_date ON indicators(trade_date);

COMMENT ON TABLE indicators IS '技术指标缓存';
COMMENT ON COLUMN indicators.indicator_type IS '指标类型（MA/MACD/RSI 等）';
COMMENT ON COLUMN indicators.indicator_value IS 'JSON 格式指标值';


-- ============================================================
-- 每日推荐记录表
-- ============================================================
CREATE TABLE IF NOT EXISTS recommendations (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL,
    recommend_date DATE NOT NULL,
    score NUMERIC(5, 2) NOT NULL,
    signals JSONB,
    reason TEXT,
    suggested_action VARCHAR(20) NOT NULL,
    risk_level VARCHAR(20),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_recommendations_code ON recommendations(code);
CREATE INDEX IF NOT EXISTS ix_recommendations_date ON recommendations(recommend_date);
CREATE INDEX IF NOT EXISTS ix_recommendations_date_score ON recommendations(recommend_date, score DESC);

COMMENT ON TABLE recommendations IS '每日推荐记录';
COMMENT ON COLUMN recommendations.score IS '综合评分（0-100）';
COMMENT ON COLUMN recommendations.signals IS '策略信号列表（JSON 数组）';
COMMENT ON COLUMN recommendations.suggested_action IS '建议动作：buy/hold/sell';
COMMENT ON COLUMN recommendations.risk_level IS '风险等级：low/medium/high';


-- ============================================================
-- 用户持仓表
-- ============================================================
CREATE TABLE IF NOT EXISTS user_positions (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL DEFAULT 'default',
    code VARCHAR(10) NOT NULL,
    buy_date DATE NOT NULL,
    buy_price NUMERIC(10, 2) NOT NULL,
    quantity INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'holding',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_user_positions_status CHECK (status IN ('holding', 'sold')),
    CONSTRAINT ck_user_positions_qty CHECK (quantity > 0),
    CONSTRAINT ck_user_positions_price CHECK (buy_price > 0)
);

CREATE INDEX IF NOT EXISTS ix_user_positions_code ON user_positions(code);
CREATE INDEX IF NOT EXISTS ix_user_positions_user_status ON user_positions(user_id, status);

COMMENT ON TABLE user_positions IS '用户持仓';
COMMENT ON COLUMN user_positions.status IS '状态：holding（持有）/sold（已卖出）';


-- ============================================================
-- 验证建表结果
-- ============================================================
-- SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;
