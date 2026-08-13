# Two 3-Day Portfolio Projects — Data Engineering / Data Analysis

Built on your current stack (Python, SQL, Power BI) plus one new skill: calling a
REST API from Python. Each project is scoped to ~3 focused days. Both fit the
Projects section of either template; Project 2 is written so it also drops
straight into the CV template's Research & Academic Projects section.

## The "one new thing": REST APIs

Calling a live API instead of only working from a downloaded CSV is the
lowest-friction addition to your stack right now — no new accounts, no
billing, no multi-day learning curve — and it upgrades the story from
"analyzed a static file" to "built a pipeline that pulls live data."
If you want a bigger stretch later, Azure Data Factory or Azure SQL Database
would tie directly to your DP-900 cert, but that adds real setup overhead
(subscription, provisioning, IAM) that doesn't fit a 3-day budget.

---

## Project 1 — Automated FX Rate Pipeline (Data Engineering angle)

**Stack:** Python (requests, sqlite3) → SQL → Power BI
**Data source:** Frankfurter API — free, no key required, ECB exchange rate
data back to 1999. Docs: https://frankfurter.dev

**Day 1 — Build the pipeline**
Run `fetch_fx_rates.py` (included). It calls Frankfurter's time-series
endpoint, backfills ~6 months of USD→EUR/GBP/JPY rates on the first run, and
writes them into a local SQLite database (`fx_rates.db`). Re-run it any time
and it only pulls the days since your last run — that incremental logic is
what makes "automated pipeline" a true claim rather than just a phrase.

**Day 2 — Analyze**
Run the queries in `analysis_queries.sql` against `fx_rates.db`:
day-over-day % change, a 7-day rolling average, the single biggest daily
swing per currency, and overall volatility range. These use window
functions (`LAG`, `AVG() OVER`, `ROW_NUMBER()`) — worth naming explicitly in
an interview, since window functions are a common SQL screening topic.

**Day 3 — Visualize + document**
Export the query results to CSV (see "Connecting SQLite to Power BI" below)
and build a Power BI report: a trend line per currency, a card showing the
biggest mover, one written takeaway. Push the code to GitHub with a short
README explaining the pipeline.

**Resume bullet formula:**
"Built an automated ETL pipeline in Python that pulls exchange-rate data via
a REST API, loads it into SQLite, and surfaces trends in Power BI — refreshes
with a single re-run instead of a manual check."

**CV framing (Research & Academic Projects section):**
- Research question: How volatile are major currency pairs against the USD
  over a 6-month window, and can a simple automated pipeline track that
  reliably?
- Method: Python + REST API for extraction, SQLite for storage, SQL window
  functions for analysis, Power BI for visualization.
- Outcome: [fill in your actual biggest finding once you've run it — e.g.
  "GBP showed the largest single-day swing at X%"]

---

## Project 2 — Retail Sales & Customer Analysis (Data Analyst angle)

**Stack:** SQL (the heavy lifting) → Python/pandas (anything SQL handles
awkwardly) → Power BI
**Data source:** the "Online Retail II" dataset (UCI Machine Learning
Repository) — real UK e-commerce transactions, 2009–2011. Kaggle's "Sample
Superstore" dataset is a fine substitute if you'd rather work with US retail
data.

**Day 1 — Load and clean**
Load the CSV into SQLite. Write SQL to handle the usual mess: nulls,
duplicate invoices, cancelled orders (flagged with a "C" prefix on the
invoice number in Online Retail II), and fix data types (dates, quantities).

**Day 2 — Analyze**
Write the queries that make this project worth showing: RFM segmentation
(Recency, Frequency, Monetary — group customers by how recently, how often,
and how much they buy), top products/categories by revenue, and
month-over-month revenue trend. This is where SQL depth shows — joins,
CTEs, `GROUP BY` with multiple aggregates.

**Day 3 — Visualize + document**
Build a Power BI report: one summary page (headline KPIs), one
customer-segment page, one product/trend page. Write 3–4 findings as plain
bullets, plus one recommendation — that summary becomes your CV's "Outcome"
line.

**Resume bullet formula:**
"Analyzed 500K+ retail transactions using SQL (RFM segmentation, revenue
trend analysis) and built a Power BI report identifying [top segment or
driver] — informed [a recommendation]."

**CV framing (Research & Academic Projects section):**
- Research question: Which customer segments and product categories drive
  the most revenue, and how does that change over time?
- Method: SQL-based RFM segmentation and time-series aggregation on
  transactional data; Power BI for visualization.
- Outcome: [your actual top finding]

---

## Connecting SQLite to Power BI

Power BI Desktop doesn't have a simple built-in SQLite connector, so don't
lose Day 3 fighting an ODBC driver. Easiest path — export your query results
to CSV and import that:

```python
import pandas as pd, sqlite3
conn = sqlite3.connect("fx_rates.db")
df = pd.read_sql("SELECT * FROM fx_rates", conn)
df.to_csv("fx_rates_export.csv", index=False)
```

Then in Power BI: **Get Data → Text/CSV**. Same approach works for Project 2.

## Setup checklist
- `pip install requests pandas`
- Power BI Desktop (free, Windows) or the Power BI service if you're on Mac
- A SQLite viewer if you want one (DB Browser for SQLite is free) — not
  required, Python handles everything above without it
