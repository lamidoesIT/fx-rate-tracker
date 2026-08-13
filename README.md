# FX Rate Tracker

A small end-to-end data pipeline for tracking foreign exchange rates — built
to practice the full extract → transform → load → visualize workflow,
including pulling from a live API for the first time.

**Live demo:** [add your Streamlit URL here]
**Repo:** github.com/lamidoesIT/fx-rate-tracker

## What it does

- Pulls historical and daily USD exchange rates (against EUR, GBP, and JPY)
  from the Frankfurter API, a free service backed by European Central Bank
  reference rates
- Stores the data in a local SQLite database, updating incrementally — each
  re-run only fetches the days since the last one instead of re-downloading
  everything
- Analyzes volatility with SQL window functions: day-over-day % change, a
  7-day rolling average, and the single biggest daily move per currency
- Visualizes the results in an interactive Streamlit dashboard, deployed live

## Why I built it

I wanted a project that covered the whole pipeline end to end, not just an
analysis of a CSV someone else already collected — a live data source,
storage, SQL-based analysis, and a working, shareable dashboard.

## How it works

- `fetch_fx_rates.py` calls Frankfurter's time-series endpoint and backfills
  about six months of rate history into `fx_rates.db` on the first run
- `analysis_queries.sql` holds the analysis queries — day-over-day change,
  rolling averages, and volatility — using `LAG`, `AVG() OVER`, and
  `ROW_NUMBER()`
- `app.py` is the Streamlit app: it fetches its own data (cached hourly),
  runs the same kind of analysis in pandas, and renders it as interactive
  charts

## What I found

[Fill this in with your actual biggest finding once you've explored the
data — e.g. "GBP showed the largest single-day swing at X% over the period"]

## Tech stack

Python (requests, pandas) · SQLite · SQL (window functions) · Streamlit

## Running it locally

```bash
pip install -r requirements.txt
python fetch_fx_rates.py
streamlit run app.py
```
