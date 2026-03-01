import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import io
import numpy as np

# Constants for NSE URLs
INDEX_URLS = {
    "Nifty 50": "https://archives.nseindia.com/content/indices/ind_nifty50list.csv",
    "Nifty 500": "https://archives.nseindia.com/content/indices/ind_nifty500list.csv",
    "Nifty Microcap 250": "https://archives.nseindia.com/content/indices/ind_niftymicrocap250_list.csv",
    "All NSE Universe": "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
}

st.set_page_config(page_title="Advanced NSE Stock Scanner", layout="wide")

st.title("🚀 Advanced NSE Stock & Momentum Scanner")
st.markdown("Scans NSE indices (or the entire universe) to calculate SMAs, Periodic Returns, Momentum, 52-Week High proximity, and filters by Traded Volume > 2 Cr.")

@st.cache_data(ttl=3600)
def fetch_index_symbols(index_name):
    url = INDEX_URLS.get(index_name)
    if not url:
        return []
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text))
        
        # 'SYMBOL' for All NSE list, 'Symbol' for Indices
        col_name = 'SYMBOL' if index_name == "All NSE Universe" else 'Symbol'
        
        if col_name in df.columns:
            return [f"{symbol.strip()}.NS" for symbol in df[col_name].tolist()]
        else:
            st.error(f"Failed to parse symbol list. Expected column '{col_name}'.")
            return []
    except Exception as e:
        st.error(f"Error fetching symbols for {index_name}: {e}")
        return []

@st.cache_data(ttl=3600)
def fetch_data(tickers):
    if not tickers:
        return pd.DataFrame(), None
        
    CHUNK_SIZE = 500
    all_data_frames = []
    
    for i in range(0, len(tickers), CHUNK_SIZE):
        chunk = tickers[i:min(i + CHUNK_SIZE, len(tickers))]
        chunk_data = yf.download(chunk, period="1y", group_by="ticker", threads=True, auto_adjust=True, progress=False)
        all_data_frames.append(chunk_data)

    if len(all_data_frames) == 1:
        data = all_data_frames[0]
    else:
        pass

    results = []
    progress_bar = st.progress(0, text="Processing calculations...")
    
    def get_ticker_df(ticker, chunk_list):
        for c in chunk_list:
            if isinstance(c.columns, pd.MultiIndex):
                if ticker in c.columns.levels[0]:
                    return c[ticker]
            else:
                if len(c.columns) > 0 and 'Close' in c.columns:
                    return c
        return pd.DataFrame()

    total_tickers = len(tickers)

    for idx, ticker in enumerate(tickers):
        if idx % 50 == 0:
             progress_bar.progress(idx / total_tickers, text=f"Calculating data for {ticker} ({idx}/{total_tickers})...")
        try:
            df = get_ticker_df(ticker, all_data_frames) if len(all_data_frames) > 1 else (data if len(tickers) == 1 else data[ticker])
            
            if df is None or df.empty:
                continue
                
            df = df.dropna(subset=['Close', 'Volume'])
            if len(df) < 5: 
                continue
            
            latest_data = df.iloc[-1]
            current_price = latest_data['Close']
            current_volume = latest_data['Volume']
            
            value_traded_cr = (current_price * current_volume) / 10000000
            
            if value_traded_cr < 2.0:
                 continue 

            df['Daily_Return'] = df['Close'].pct_change()

            def get_momentum(days):
                if len(df) >= days:
                    recent = df['Daily_Return'].tail(days)
                    mean_ret = recent.mean()
                    std_ret = recent.std()
                    return mean_ret / std_ret if std_ret > 0 else 0
                return np.nan

            mom_3m = get_momentum(63)
            mom_1m = get_momentum(21)
            mom_5d = get_momentum(5)
            mom_1d = get_momentum(1) 

            def get_period_return(days):
                if len(df) >= days:
                    return (current_price / df['Close'].iloc[-days]) - 1
                return np.nan

            ret_1y = get_period_return(min(252, len(df))) 
            ret_3m = get_period_return(63)
            ret_1m = get_period_return(21)
            ret_5d = get_period_return(5)
            ret_1d = get_period_return(2) 

            sma20 = df['Close'].tail(20).mean() if len(df) >= 20 else np.nan
            sma50 = df['Close'].tail(50).mean() if len(df) >= 50 else np.nan
            sma200 = df['Close'].tail(200).mean() if len(df) >= 200 else np.nan

            ma_rank = 1 if (pd.notna(sma20) and pd.notna(sma50) and pd.notna(sma200) and (sma20 > sma50 > sma200)) else 0

            recent_252 = df['Close'].tail(252)
            high_52w = recent_252.max()
            away_from_52wh = (current_price / high_52w) - 1 if high_52w > 0 else np.nan

            def is_valid(val):
                return pd.notna(val)

            results.append({
                'Ticker': ticker.replace('.NS', ''),
                'Close (₹)': round(current_price, 2) if is_valid(current_price) else None,
                'Value Traded (Cr)': round(value_traded_cr, 2),
                'MA Rank (20>50>200)': ma_rank,
                'Close > 20': current_price > sma20 if is_valid(sma20) else False,
                '20 SMA': round(sma20, 2) if is_valid(sma20) else None,
                '50 SMA': round(sma50, 2) if is_valid(sma50) else None,
                '200 SMA': round(sma200, 2) if is_valid(sma200) else None,
                '52W High': round(high_52w, 2) if is_valid(high_52w) else None,
                'Dist from 52WH': away_from_52wh,
                '1D Ret': ret_1d,
                '5D Ret': ret_5d,
                '1M Ret': ret_1m,
                '3M Ret': ret_3m,
                '1Y Ret': ret_1y,
                'Mom 5D': round(mom_5d, 4) if is_valid(mom_5d) else None,
                'Mom 1M': round(mom_1m, 4) if is_valid(mom_1m) else None,
                'Mom 3M': round(mom_3m, 4) if is_valid(mom_3m) else None
            })
        except Exception as e:
            pass 
    
    progress_bar.progress(1.0, text="Calculations complete!")
            
    res_df = pd.DataFrame(results)
    
    if not res_df.empty:
        res_df['Rnk_52WH'] = res_df['Dist from 52WH'].rank(ascending=False)
        res_df['Rnk_Mom3M'] = res_df['Mom 3M'].rank(ascending=False)
        res_df['Combined Rank'] = ((res_df['Rnk_52WH'] + res_df['Rnk_Mom3M']) / 2).rank(ascending=True)

    return res_df, all_data_frames

st.sidebar.header("Scanner Configuration")
selected_index = st.sidebar.selectbox("Select Universe to Scan (Filtered by > 2 Cr Traded Value):", list(INDEX_URLS.keys()), index=0)

if st.sidebar.button(f"Scan {selected_index}"):
    st.session_state['scan_triggered'] = True
    st.session_state['selected_index_scan'] = selected_index

if st.session_state.get('scan_triggered', False):
    current_scan = st.session_state.get('selected_index_scan', selected_index)
    
    if current_scan == "All NSE Universe":
        st.info("Scanning the entire NSE Universe (~2200+ stocks). This will take a few minutes to download from Yahoo Finance. Please be patient...")
        
    with st.spinner(f"Fetching {current_scan} symbols..."):
        tickers = fetch_index_symbols(current_scan)
        
    if tickers:
        summary_df, raw_data_frames = fetch_data(tickers)
        
        if summary_df is not None and not summary_df.empty:
            st.session_state['summary_df'] = summary_df
            st.session_state['raw_data_frames'] = raw_data_frames
            st.session_state['tickers'] = tickers
            st.success(f"Successfully processed {len(summary_df)} stocks from {current_scan} that passed the > 2 Cr volume threshold!")
        else:
            st.warning("Data fetched but no valid records met the criteria (or API blocked).")
    else:
        st.error(f"Failed to load symbols for {current_scan}.")

if 'summary_df' in st.session_state and not st.session_state['summary_df'].empty:
    summary_df = st.session_state['summary_df'].copy()
    
    st.markdown("---")
    current_scan = st.session_state.get('selected_index_scan', selected_index)
    st.subheader(f"📊 {current_scan} Screener Results (> 2 Cr Traded Value)")
    
    sort_by = st.selectbox("Sort Results By:", [
        "Combined Rank",
        "Dist from 52WH (Closest First)", 
        "Mom 3M (Highest First)",
        "3M Ret (Highest First)",
        "1Y Ret (Highest First)",
        "Value Traded (Cr) (Highest First)"
    ])
    
    if sort_by == "Combined Rank":
        summary_df = summary_df.sort_values(by="Combined Rank", ascending=True)
    elif sort_by == "Dist from 52WH (Closest First)":
        summary_df = summary_df.sort_values(by="Dist from 52WH", ascending=False)
    elif sort_by == "Mom 3M (Highest First)":
        summary_df = summary_df.sort_values(by="Mom 3M", ascending=False)
    elif sort_by == "3M Ret (Highest First)":
        summary_df = summary_df.sort_values(by="3M Ret", ascending=False)
    elif sort_by == "1Y Ret (Highest First)":
        summary_df = summary_df.sort_values(by="1Y Ret", ascending=False)
    elif sort_by == "Value Traded (Cr) (Highest First)":
        summary_df = summary_df.sort_values(by="Value Traded (Cr)", ascending=False)

    def format_pct(val):
        if pd.isna(val): return "-"
        return f"{val:.2%}"

    display_cols = [
        'Combined Rank', 'Ticker', 'Close (₹)', 'Value Traded (Cr)', 
        'MA Rank (20>50>200)', 'Close > 20', 'Dist from 52WH',
        '1D Ret', '5D Ret', '1M Ret', '3M Ret', '1Y Ret',
        'Mom 5D', 'Mom 1M', 'Mom 3M'
    ]
    
    st.dataframe(
        summary_df[display_cols].style.applymap(
            lambda val: 'color: green' if val == 1 else ('color: gray' if val == 0 else ''), 
            subset=['MA Rank (20>50>200)']
        ).applymap(
            lambda val: 'color: green' if val else 'color: red',
            subset=['Close > 20']
        ).applymap(
            lambda val: 'color: green' if val > 0 else ('color: red' if val < 0 else ''),
            subset=['1D Ret', '5D Ret', '1M Ret', '3M Ret', '1Y Ret']
        ).format({
            'Dist from 52WH': format_pct,
            '1D Ret': format_pct,
            '5D Ret': format_pct,
            '1M Ret': format_pct,
            '3M Ret': format_pct,
            '1Y Ret': format_pct,
            'Combined Rank': "{:.0f}"
        }, na_rep="-"),
        use_container_width=True, 
        hide_index=True,
        height=600
    )
    
    st.markdown("---")
    st.subheader("Interactive Stock Chart")
    
    selected_ticker = st.selectbox("Select a stock to view its chart:", summary_df['Ticker'])
    
    stock_yf_ticker = f"{selected_ticker}.NS"
    
    def get_single_df(ticker, chunk_list):
        for c in chunk_list:
            if isinstance(c.columns, pd.MultiIndex):
                if ticker in c.columns.levels[0]:
                    return c[ticker]
            else:
                if len(c.columns) > 0 and 'Close' in c.columns:
                    return c
        return pd.DataFrame()

    stock_df = get_single_df(stock_yf_ticker, st.session_state['raw_data_frames'])

    if stock_df is not None and not stock_df.empty:
        stock_df = stock_df.dropna(subset=['Close'])
        stock_df['SMA_20'] = stock_df['Close'].rolling(window=20).mean()
        stock_df['SMA_50'] = stock_df['Close'].rolling(window=50).mean()
        stock_df['SMA_200'] = stock_df['Close'].rolling(window=200).mean()
        
        fig = go.Figure()
        
        fig.add_trace(go.Candlestick(
            x=stock_df.index, open=stock_df['Open'], high=stock_df['High'],
            low=stock_df['Low'], close=stock_df['Close'], name='Price'
        ))
        
        fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['SMA_20'], line=dict(color='orange', width=1), name='SMA 20'))
        fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['SMA_50'], line=dict(color='blue', width=1), name='SMA 50'))
        fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['SMA_200'], line=dict(color='red', width=2), name='SMA 200'))
        
        fig.update_layout(
            title=f"{selected_ticker} Price & Moving Averages",
            yaxis_title='Price (₹)',
            xaxis_title='Date',
            xaxis_rangeslider_visible=False,
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
