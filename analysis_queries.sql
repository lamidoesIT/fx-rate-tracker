-- analysis_queries.sql
-- Example analysis queries for fx_rates.db (produced by fetch_fx_rates.py)
-- Open fx_rates.db in DB Browser for SQLite (free) or run:
--   sqlite3 fx_rates.db
--   .read analysis_queries.sql

-- 1. Day-over-day percentage change per currency
SELECT
    rate_date,
    target_currency,
    rate,
    ROUND(
        (rate - LAG(rate) OVER (PARTITION BY target_currency ORDER BY rate_date))
        / LAG(rate) OVER (PARTITION BY target_currency ORDER BY rate_date) * 100
    , 3) AS pct_change_from_prev_day
FROM fx_rates
ORDER BY target_currency, rate_date;


-- 2. 7-day rolling average rate per currency (smooths out daily noise)
SELECT
    rate_date,
    target_currency,
    rate,
    ROUND(AVG(rate) OVER (
        PARTITION BY target_currency
        ORDER BY rate_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 4) AS rolling_7day_avg
FROM fx_rates
ORDER BY target_currency, rate_date;


-- 3. Biggest single-day swing (up or down) per currency
WITH daily_change AS (
    SELECT
        rate_date,
        target_currency,
        rate,
        rate - LAG(rate) OVER (PARTITION BY target_currency ORDER BY rate_date) AS change
    FROM fx_rates
),
ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY target_currency ORDER BY ABS(change) DESC) AS rn
    FROM daily_change
    WHERE change IS NOT NULL
)
SELECT target_currency, rate_date, rate, change
FROM ranked
WHERE rn = 1
ORDER BY ABS(change) DESC;


-- 4. Overall range per currency across the whole period (a simple volatility measure)
SELECT
    target_currency,
    MIN(rate) AS lowest_rate,
    MAX(rate) AS highest_rate,
    ROUND(MAX(rate) - MIN(rate), 4) AS range_abs,
    ROUND((MAX(rate) - MIN(rate)) / MIN(rate) * 100, 2) AS range_pct
FROM fx_rates
GROUP BY target_currency
ORDER BY range_pct DESC;
