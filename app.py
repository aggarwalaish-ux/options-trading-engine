import streamlit as st
import sys
import os

# ✅ FIX: Ensure local modules are found (critical for Streamlit Cloud)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pipeline import run_pipeline

# Page config
st.set_page_config(page_title="Options Trading Engine", layout="wide")

st.title("📈 Options Trading Engine (Open Source Data)")
st.caption("RL-based signal engine for NIFTY stocks")

# Run button
if st.button("Run Strategy"):
    with st.spinner("Running strategy... this may take 1-2 mins ⏳"):
        try:
            results_df, trades_df = run_pipeline()

            st.session_state["results"] = results_df
            st.session_state["trades"] = trades_df

            st.success("✅ Strategy run completed!")

        except Exception as e:
            st.error("❌ Error occurred while running pipeline")
            st.exception(e)

# Show results
if "results" in st.session_state:

    df = st.session_state["results"]

    st.subheader("📊 All Signals")
    st.dataframe(df)

    # Top trades
    st.subheader("🔥 Top Trades")

    top = df[df["Signal"] != "NO TRADE"] \
        .sort_values(by="Confidence", ascending=False) \
        .head(5)

    st.dataframe(top)

    # Download button
    st.download_button(
        label="⬇️ Download Signals CSV",
        data=df.to_csv(index=False),
        file_name="signals.csv",
        mime="text/csv"
    )

# Trade log
if "trades" in st.session_state:
    st.subheader("📉 Trade Log")

    trades_df = st.session_state["trades"]

    if not trades_df.empty:
        st.dataframe(trades_df)

        # Simple visualization
        if "Confidence" in trades_df.columns:
            st.subheader("📈 Confidence Trend")
            st.line_chart(trades_df["Confidence"])
    else:
        st.info("No trades executed yet.")
