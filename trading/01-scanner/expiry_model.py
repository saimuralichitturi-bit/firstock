import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import feedparser
from bs4 import BeautifulSoup

load_dotenv()

st.set_page_config(page_title="Nifty Expiry Probability", layout="wide")

page = st.sidebar.radio("Navigation", ["📉 Expiry Model & AI Insight", "📰 Live Financial News"])

if page == "📰 Live Financial News":
    st.title("📰 Live Financial News Aggregator")
    st.markdown("Real-time headlines combined from top Indian financial sources.")
    
    @st.cache_data(ttl=900)
    def fetch_news():
        feeds = {
            "Economic Times": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
            "Moneycontrol": "https://www.moneycontrol.com/rss/MCtopnews.xml",
            "CNBC TV18": "https://www.cnbctv18.com/commonfeeds/v1/cne/rss/market.xml",
            "NDTV Profit": "https://feeds.feedburner.com/ndtvprofit-latest"
        }
        
        news_data = []
        for source, url in feeds.items():
            try:
                parsed = feedparser.parse(url)
                for entry in parsed.entries[:12]:
                    summary = entry.get("summary", "")
                    if summary:
                        summary = BeautifulSoup(summary, "html.parser").get_text().strip()
                        summary = summary[:200] + "..." if len(summary) > 200 else summary
                        
                    news_data.append({
                        "Source": source,
                        "Title": entry.get("title", "No Title"),
                        "Link": entry.get("link", "#"),
                        "Published": entry.get("published", ""),
                        "Summary": summary
                    })
            except Exception as e:
                pass
                
        return pd.DataFrame(news_data)

    with st.spinner("Fetching latest news from ET, Moneycontrol, CNBC TV18, and NDTV Profit..."):
        df_news = fetch_news()

    if not df_news.empty:
        st.subheader("🤖 AI Real-Time Market Sentiment")
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if api_key:
            if st.button("Analyze Current News Sentiment"):
                with st.spinner("Analyzing top headlines with DeepSeek LLM..."):
                    try:
                        from openai import OpenAI
                        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
                        
                        top_headlines = "\n".join([f"- {row.Title}" for row in df_news.head(20).itertuples()])
                        prompt = f"Analyze the following recent financial headlines and provide a brief overall market sentiment (Bullish, Bearish, or Neutral) with a short 2-3 sentence justification:\n\n{top_headlines}"
                        
                        response = client.chat.completions.create(
                            model="deepseek-chat",
                            messages=[
                                {"role": "system", "content": "You are a top-tier quantitative hedge fund analyst."},
                                {"role": "user", "content": prompt}
                            ],
                            max_tokens=150
                        )
                        st.success(f"**Market Sentiment:**\n\n{response.choices[0].message.content.strip()}")
                    except Exception as e:
                        st.error(f"Failed to generate sentiment analysis: {e}")
        else:
            st.info("Set DEEPSEEK_API_KEY in your .env file to enable AI Sentiment Analysis on Live News.")
            
        st.markdown("---")
        
        # Sort by source for grouping (or by date if parsed properly)
        for source in df_news['Source'].unique():
            st.markdown(f"### 🟩 {source}")
            source_news = df_news[df_news['Source'] == source]
            
            # Create a 3-column grid for news cards
            cols = st.columns(3)
            for index, row in enumerate(source_news.itertuples()):
                col = cols[index % 3]
                with col:
                    st.markdown(f"""
                    <div style="padding:15px; border-radius:10px; background-color:#1e1e1e; margin-bottom:15px; border-left: 4px solid #58a6ff;">
                        <h4 style="margin-top:0px;margin-bottom:10px;"><a href="{row.Link}" target="_blank" style="color:#c9d1d9;text-decoration:none;">{row.Title}</a></h4>
                        <p style="font-size:12px;color:#8b949e;margin-bottom:5px;">🕒 {row.Published}</p>
                        <p style="font-size:14px;color:#c9d1d9;">{row.Summary}</p>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown("---")
    else:
        st.error("Failed to fetch news data. Please try again later.")
    
    st.stop() # Stops execution here so it doesn't render the rest of the expiry model

st.title("📊 Nifty 50 Weekly Expiry Probability Model")
st.markdown("Calculates historical probability percentiles for Nifty moves from **Wednesday Open** to **Tuesday Close** (the standard weekly expiry lifecycle).")

@st.cache_data(ttl=3600*24) # Cache for 24 hours as this is historical
def fetch_and_process_expiry_data(years=10):
    # 1. Fetch Nifty data
    ticker = "^NSEI"
    df = yf.download(ticker, period=f"{years}y", interval="1d", auto_adjust=True, progress=False)
    
    if df.empty:
        st.error("Could not fetch Nifty data from Yahoo Finance.")
        return None
    
    # Flatten multi-index if necessary (yfinance sometimes nests)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    df = df[['Open', 'High', 'Low', 'Close']].dropna()
    df['Weekday'] = df.index.dayofweek 
    
    # Group into "Expiry Cycles" (Wednesday -> Tuesday)
    expiry_ids = []
    
    for idx in range(len(df)):
        current_date = df.index[idx]
        shifted_date = current_date - timedelta(days=2)
        yr, wk, _ = shifted_date.isocalendar()
        expiry_ids.append(f"{yr}-W{wk:02d}")
        
    df['Expiry_Cycle_ID'] = expiry_ids
    
    # Aggregate by Cycle
    results = []
    for cycle_id, group in df.groupby('Expiry_Cycle_ID'):
        if len(group) < 2: 
            continue # Ignore cycles with only 1 trading day (e.g., current active cycle if just started)
            
        start_date = group.index[0]
        end_date = group.index[-1]
        start_open = float(group['Open'].iloc[0])
        end_close = float(group['Close'].iloc[-1])
        
        max_high = float(group['High'].max())
        min_low = float(group['Low'].min())
        
        pct_change = (end_close / start_open) - 1
        abs_pct_change = abs(pct_change)
        
        results.append({
            'Cycle ID': cycle_id,
            'Start Date': start_date.strftime('%Y-%m-%d'),
            'End Date': end_date.strftime('%Y-%m-%d'),
            'Days Traded': len(group),
            'Wed Open': start_open,
            'Tue Close': end_close,
            'Max High': max_high,
            'Min Low': min_low,
            'Return %': pct_change,
            'Abs Return %': abs_pct_change
        })
        
    return pd.DataFrame(results), df

st.sidebar.header("Configuration")
years_to_analyze = st.sidebar.slider("Historical Data to Analyze (Years)", min_value=1, max_value=20, value=10, step=1)

with st.spinner("Downloading historical Nifty data & calculating percentiles..."):
     cycle_df, raw_df = fetch_and_process_expiry_data(years=years_to_analyze)
     
if cycle_df is not None and not cycle_df.empty:
    total_weeks = len(cycle_df)
    st.success(f"Successfully processed {total_weeks} weekly expiry cycles over {years_to_analyze} years.")
    
    # Calculate Percentiles
    percentile_levels = [10, 25, 50, 75, 80, 90, 95, 99]
    
    # Absolute movement (Magnitude)
    abs_percentiles = np.percentile(cycle_df['Abs Return %'] * 100, percentile_levels)
    
    # Directional (Upside vs Downside)
    upside_moves = cycle_df[cycle_df['Return %'] > 0]['Return %'] * 100
    downside_moves = cycle_df[cycle_df['Return %'] < 0]['Return %'] * 100
    
    up_perc = np.percentile(upside_moves, percentile_levels) if not upside_moves.empty else [0]*len(percentile_levels)
    down_perc = np.percentile(downside_moves.abs(), percentile_levels) if not downside_moves.empty else [0]*len(percentile_levels) 
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
         st.subheader("📊 Movement Probabilities (Magnitude)")
         st.markdown("This answers: *'Historically, what percentage of the time does Nifty move less than X% from Wed Open to Tue Close?'*")
         
         prob_df = pd.DataFrame({
             'Probability (Percentile)': [f"{p}% of the time" for p in percentile_levels],
             'Max Movement (+/- %)': [f"Moves less than {val:.2f}%" for val in abs_percentiles]
         })
         st.dataframe(prob_df, hide_index=True, use_container_width=True)
         
    with col2:
         st.subheader("📈 Directional Breakdown")
         st.markdown("Comparing upside rallies vs downside crashes magnitude.")
         dir_df = pd.DataFrame({
             'Percentile': [f"{p}th Percentile" for p in percentile_levels],
             'Upside (+%)': [f"+{val:.2f}%" for val in up_perc],
             'Downside (-%)': [f"-{val:.2f}%" for val in down_perc]
         })
         st.dataframe(dir_df, hide_index=True, use_container_width=True)

    st.markdown("---")
    
    # Current Active Week Box
    st.subheader("🔥 Current Active Week Status")
    current_cycle_id = cycle_df.iloc[-1]['Cycle ID']
    active_group = raw_df[raw_df['Expiry_Cycle_ID'] == current_cycle_id]
    
    if not active_group.empty:
        curr_open = active_group['Open'].iloc[0]
        curr_last = active_group['Close'].iloc[-1]
        curr_pct = (curr_last / curr_open) - 1
        curr_abs = abs(curr_pct) * 100
        
        # Find what percentile this currently sits at
        current_percentile = (cycle_df['Abs Return %'] * 100 < curr_abs).mean() * 100
        
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        metric_col1.metric("Wed Open Price", f"{curr_open:.2f}")
        metric_col2.metric("Current Live/Close Price", f"{curr_last:.2f}")
        metric_col3.metric("Current Move", f"{curr_pct*100:.2f}%")
        metric_col4.metric("Current Implied Percentile", f"{current_percentile:.1f}th")
        
        st.info(f"The current week's move of **{curr_pct*100:.2f}%** ranks in the **{current_percentile:.1f}th percentile** historically.")

    # Distribution Chart
    st.subheader("Historical Distribution Curve (Wed Open to Tue Close)")
    fig = px.histogram(
         cycle_df, 
         x="Return %", 
         nbins=100,
         title="Distribution of Nifty Weekly Expiry Returns",
         labels={'Return %': 'Percentage Return (Wed->Tue)', 'count': 'Number of Weeks'},
         color_discrete_sequence=['#1f77b4']
    )
    # Format X axis to percentage
    fig.layout.xaxis.tickformat = '.1%'
    # Add 50th and 90th percentile bounds
    abs_50 = abs_percentiles[2] / 100
    abs_90 = abs_percentiles[5] / 100
    fig.add_vline(x=abs_90, line_dash="dash", line_color="red", annotation_text="90th %ile", annotation_position="top right")
    fig.add_vline(x=-abs_90, line_dash="dash", line_color="red", annotation_text="90th %ile", annotation_position="top left")
    
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("🧠 DeepSeek AI Quantitative Analysis")
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if api_key:
        if st.button("Generate DeepSeek Insight on Current Cycle"):
            with st.spinner("Analyzing historical distribution and current market posture with DeepSeek LLM..."):
                try:
                    from openai import OpenAI
                    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
                    
                    context = (
                        f"Nifty 50 Statistical Profile ({years_to_analyze} Years):\n"
                        f"- 50th Percentile (Median) absolute move: {abs_percentiles[2]:.2f}%\n"
                        f"- 90th Percentile (Tail Risk) absolute move: {abs_percentiles[5]:.2f}%\n"
                    )
                    
                    if not active_group.empty:
                        context += (
                            f"\nCurrent Active Cycle Status:\n"
                            f"- Current move so far: {curr_pct*100:.2f}%\n"
                            f"- This implies the {current_percentile:.1f}th historical percentile.\n"
                        )
                    
                    prompt = f"You are a quantitative options trader. Analyze this structural data regarding the Nifty 50 weekly expiry cycle (Wednesday Open to Tuesday Close).\n\n{context}\n\nProvide actionable insights on implied volatility, mean reversion probability, and optimal option selling/buying strategies considering this specific statistical posture. Keep it under 200 words and highly technical."
                    
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": "You are a top-tier quantitative researcher analyzing market volatility risk premia."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=300
                    )
                    insight_text = response.choices[0].message.content.strip()
                    st.success(f"**DeepSeek Quantitative Breakdown:**\n\n{insight_text}")
                except Exception as e:
                    st.error(f"Failed to generate DeepSeek insight: {e}")
    else:
        st.info("Set DEEPSEEK_API_KEY in your .env file to unlock on-demand quantitative AI analysis of the Nifty expiry cycle.")
