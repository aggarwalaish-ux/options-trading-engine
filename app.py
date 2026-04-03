import streamlit as st
import sys
import os
import pandas as pd

# ✅ FIX: Ensure local modules are found (critical for Streamlit Cloud)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pipeline import run_pipeline
from data_fetcher import fetch_ohlcv, fetch_option_chain
from config import NIFTY_50

# Page config
st.set_page_config(page_title="Options Trading Engine", layout="wide")

st.title("📈 Options Trading Engine (Open Source Data)")
st.caption("RL-based signal engine for NIFTY stocks")

# ===== RAW DATA EXPLORATION SECTION =====
st.sidebar.markdown("### 📊 Data Explorer")

with st.sidebar.expander("🔍 View Raw Data", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        selected_ticker = st.selectbox(
            "Select a ticker:",
             NIFTY_50  # ✅ FIX: Show ALL 50 NIFTY tickers
        )
    
    with col2:
        data_type = st.radio("Data Type:", ["📈 Stock Data", "📊 Options Data"])
    
    if st.button("📥 Fetch Raw Data", key="fetch_raw"):
        try:
            if data_type == "📈 Stock Data":
                st.subheader(f"📈 {selected_ticker} - OHLCV Data (Last 5 Years)")
                stock_data = fetch_ohlcv(selected_ticker)
                
                # Display last 20 rows
                st.write(f"**Total Records:** {len(stock_data)}")
                st.dataframe(stock_data.tail(20), use_container_width=True)
                
                # Download button
                csv_data = stock_data.to_csv()
                st.download_button(
                    label="⬇️ Download Stock Data (CSV)",
                    data=csv_data,
                    file_name=f"{selected_ticker}_ohlcv_5years.csv",
                    mime="text/csv",
                    key="download_stock"
                )
                
                # Statistics
                with st.expander("📊 Statistics"):
                    st.write(stock_data.describe())
            
            else:
                st.subheader(f"📊 {selected_ticker} - Options Chain Data")
                with st.spinner("Fetching options data from NSE..."):
                    calls, puts, expiries = fetch_option_chain(selected_ticker)
                
                if calls or puts:
                    # Display expiries
                    if expiries:
                        st.write(f"**Available Expiries:** {', '.join(expiries[:5])}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**📞 Call Options (Top 5 by Strike)**")
                        if calls:
                            calls_df = pd.DataFrame(calls).T.head(5)
                            st.dataframe(calls_df, use_container_width=True)
                            
                            # Download calls
                            st.download_button(
                                label="⬇️ Download Call Options",
                                data=calls_df.to_csv(),
                                file_name=f"{selected_ticker}_calls.csv",
                                mime="text/csv",
                                key="download_calls"
                            )
                        else:
                            st.info("No call options data available")
                    
                    with col2:
                        st.write("**🔻 Put Options (Top 5 by Strike)**")
                        if puts:
                            puts_df = pd.DataFrame(puts).T.head(5)
                            st.dataframe(puts_df, use_container_width=True)
                            
                            # Download puts
                            st.download_button(
                                label="⬇️ Download Put Options",
                                data=puts_df.to_csv(),
                                file_name=f"{selected_ticker}_puts.csv",
                                mime="text/csv",
                                key="download_puts"
                            )
                        else:
                            st.info("No put options data available")
                else:
                    st.warning("⚠️ No options data available for this ticker. NSE API may be temporarily unavailable.")
        
        except Exception as e:
            st.error(f"❌ Error fetching data: {str(e)}")
            st.info("💡 Tip: This could be due to network issues or NSE API availability. Please try again.")

st.markdown("---")

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
    st.dataframe(df, use_container_width=True)

    # Top trades
    st.subheader("🔥 Top Trades")

    top = df[df["Signal"] != "NO TRADE"] \
        .sort_values(by="Confidence", ascending=False) \
        .head(5)

    st.dataframe(top, use_container_width=True)

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
        st.dataframe(trades_df, use_container_width=True)

        # Simple visualization
        if "Confidence" in trades_df.columns:
            st.subheader("📈 Confidence Trend")
            st.line_chart(trades_df["Confidence"])
    else:
        st.info("No trades executed yet.")
