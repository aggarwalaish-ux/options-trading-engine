import streamlit as st
import sys
import os
import pandas as pd

# ✅ Fix module path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pipeline import run_pipeline
from data_fetcher import fetch_ohlcv
from config import NIFTY_50
from nse_fetcher import fetch_nifty_option_chain

# =========================
# ⚙️ PAGE CONFIG
# =========================
st.set_page_config(page_title="Options Trading Engine", layout="wide")

st.title("📈 Options Trading Engine")
st.caption("Stock Direction + NIFTY Options (PCR & IV) based strategy")

# =========================
# 📊 SIDEBAR — DATA EXPLORER
# =========================
st.sidebar.markdown("### 📊 Data Explorer")

with st.sidebar.expander("🔍 Stock Data", expanded=False):
    selected_ticker = st.selectbox("Select ticker:", NIFTY_50)

    if st.button("📥 Fetch Stock Data"):
        try:
            stock_data = fetch_ohlcv(selected_ticker)

            st.subheader(f"{selected_ticker} OHLCV Data")
            st.write(f"Records: {len(stock_data)}")

            st.dataframe(stock_data.tail(20), use_container_width=True)

            st.download_button(
                "⬇️ Download CSV",
                stock_data.to_csv(),
                f"{selected_ticker}.csv",
                "text/csv",
            )

        except Exception as e:
            st.error(f"Error: {e}")

# =========================
# 📊 SIDEBAR — NIFTY OPTIONS
# =========================
st.sidebar.markdown("### 📊 NIFTY Options")

if st.sidebar.button("Fetch NIFTY Options"):

    with st.spinner("Fetching NIFTY option chain..."):
        try:
            calls, puts, expiries = fetch_nifty_option_chain()

            if calls is not None and not calls.empty:

                st.subheader("📊 NIFTY Option Chain")

                col1, col2 = st.columns(2)

                with col1:
                    st.write("📞 Calls (Top 10 by OI)")
                    top_calls = calls.sort_values("openInterest", ascending=False).head(10)
                    st.dataframe(top_calls, use_container_width=True)

                with col2:
                    st.write("🔻 Puts (Top 10 by OI)")
                    top_puts = puts.sort_values("openInterest", ascending=False).head(10)
                    st.dataframe(top_puts, use_container_width=True)

                # Metrics
                total_call_oi = calls["openInterest"].sum()
                total_put_oi = puts["openInterest"].sum()
                pcr = total_put_oi / (total_call_oi + 1e-6)
                avg_iv = calls["impliedVolatility"].mean()

                st.markdown("### 📊 Market Metrics")
                m1, m2 = st.columns(2)
                m1.metric("PCR", round(pcr, 2))
                m2.metric("Avg IV", round(avg_iv, 2))

            else:
                st.warning("No NIFTY options data available")

        except Exception as e:
            st.error(f"Error fetching NIFTY data: {e}")

st.markdown("---")

# =========================
# ▶️ RUN STRATEGY
# =========================
if st.button("🚀 Run Strategy"):
    with st.spinner("Running strategy..."):
        try:
            results_df, trades_df = run_pipeline()

            st.session_state["results"] = results_df
            st.session_state["trades"] = trades_df

            st.success("✅ Strategy completed")

        except Exception as e:
            st.error("❌ Pipeline error")
            st.exception(e)

# =========================
# 📊 RESULTS
# =========================
if "results" in st.session_state:

    df = st.session_state["results"]

    if not df.empty:

        # =========================
        # 🌍 MARKET CONTEXT
        # =========================
        st.subheader("🌍 Market Context (NIFTY Options)")

        avg_pcr = df["PCR"].iloc[0]
        avg_iv = df["IV"].iloc[0]
        market_bias = df["Market Bias"].iloc[0]

        col1, col2, col3 = st.columns(3)

        col1.metric("PCR", round(avg_pcr, 2))
        col2.metric("IV", round(avg_iv, 2))
        col3.metric("Market Bias", market_bias)

        st.markdown("---")

        # =========================
        # 📊 SIGNAL TABLE
        # =========================
        st.subheader("📊 Trading Signals")

        st.dataframe(df, use_container_width=True)

        # =========================
        # 🔥 TOP TRADES
        # =========================
        st.subheader("🔥 Top Trades")

        top = df[
            (df["Signal"] != "NO TRADE") &
            (df["Confidence"] > 0.5)
        ].sort_values(by="Confidence", ascending=False).head(5)

        st.dataframe(top, use_container_width=True)

        # =========================
        # ⬇️ DOWNLOAD
        # =========================
        st.download_button(
            "⬇️ Download Signals",
            df.to_csv(index=False),
            "signals.csv",
            "text/csv"
        )

    else:
        st.warning("No results generated")

# =========================
# 📉 TRADE LOG
# =========================
if "trades" in st.session_state:

    st.subheader("📉 Trade Log")

    trades_df = st.session_state["trades"]

    if not trades_df.empty:
        st.dataframe(trades_df, use_container_width=True)

        if "Confidence" in trades_df.columns:
            st.subheader("📈 Confidence Trend")
            st.line_chart(trades_df["Confidence"])
    else:
        st.info("No trades executed yet.")
