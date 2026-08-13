import streamlit as st
import pandas as pd
import requests
from datetime import date, timedelta

st.set_page_config(page_title="FX Rate Tracker", layout="wide")

API_ROOT = "https://api.frankfurter.dev/v1"


@st.cache_data(ttl=3600)  # re-fetch at most once per hour, so the app stays fast
def fetch_rates(base, symbols, lookback_days):
    """Pull a time series of exchange rates from the Frankfurter API
    and return it as a tidy DataFrame with columns: date, currency, rate."""
    end = date.today()
    start = end - timedelta(days=lookback_days)
    url = f"{API_ROOT}/{start.isoformat()}..{end.isoformat()}"
    params = {"base": base, "symbols": ",".join(symbols)}
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    payload = resp.json()

    rows = []
    for rate_date, currency_rates in payload.get("rates", {}).items():
        for currency, rate in currency_rates.items():
            rows.append({"date": rate_date, "currency": currency, "rate": rate})

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values(["currency", "date"])


def add_analysis_columns(df):
    """Same analysis as analysis_queries.sql (day-over-day % change,
    7-day rolling average) expressed in pandas instead of SQL."""
    df = df.copy()
    df["pct_change"] = df.groupby("currency")["rate"].pct_change() * 100
    df["rolling_7day_avg"] = (
        df.groupby("currency")["rate"]
        .transform(lambda s: s.rolling(window=7, min_periods=1).mean())
    )
    return df


st.title("FX rate tracker")
st.caption(
    "Live exchange-rate pipeline: Python + pandas, data from the Frankfurter "
    "API (European Central Bank reference rates), deployed with Streamlit."
)

with st.sidebar:
    st.header("Settings")
    base = st.selectbox("Base currency", ["USD", "EUR", "GBP"], index=0)
    all_symbols = ["EUR", "GBP", "JPY", "AUD", "CAD", "CHF"]
    default_symbols = [s for s in ["EUR", "GBP", "JPY"] if s != base]
    symbols = st.multiselect(
        "Compare against", [s for s in all_symbols if s != base], default=default_symbols
    )
    lookback_days = st.slider("Days of history", 30, 365, 180)

if not symbols:
    st.warning("Pick at least one currency to compare in the sidebar.")
    st.stop()

df = fetch_rates(base, tuple(symbols), lookback_days)
df = add_analysis_columns(df)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"{base} exchange rate over time")
    chart_df = df.pivot(index="date", columns="currency", values="rate")
    st.line_chart(chart_df)

with col2:
    st.subheader("Biggest single-day move")
    biggest = df.loc[df["pct_change"].abs().idxmax()]
    st.metric(
        label=f"{biggest['currency']} on {biggest['date'].date()}",
        value=f"{biggest['rate']:.4f}",
        delta=f"{biggest['pct_change']:.2f}%",
    )

    st.subheader("Latest rates")
    latest = (
        df.sort_values("date")
        .groupby("currency")
        .tail(1)[["currency", "rate", "pct_change"]]
        .set_index("currency")
    )
    st.dataframe(latest, width="stretch")

st.subheader("7-day rolling average")
rolling_chart_df = df.pivot(index="date", columns="currency", values="rolling_7day_avg")
st.line_chart(rolling_chart_df)

st.caption(
    "Data refreshes automatically from the Frankfurter API (cached for 1 hour). "
    "Source: European Central Bank reference rates."
)
