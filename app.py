import streamlit as st
from pipeline import run_pipeline

st.set_page_config(layout="wide")

st.title("📈 Options Trading Engine (Open Source Data)")

if st.button("Run Strategy"):
    with st.spinner("Running..."):
        results_df, trades_df = run_pipeline()

        st.session_state["results"] = results_df
        st.session_state["trades"] = trades_df

if "results" in st.session_state:

    st.subheader("📊 All Signals")
    st.dataframe(st.session_state["results"])

    st.subheader("🔥 Top Trades")
    top = st.session_state["results"][
        st.session_state["results"]["Signal"] != "NO TRADE"
    ].sort_values(by="Confidence", ascending=False).head(5)

    st.dataframe(top)

if "trades" in st.session_state:
    st.subheader("📉 Trade Log")
    st.dataframe(st.session_state["trades"])
