import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import concurrent.futures
import logging
from datetime import datetime, timedelta
import time
import os
from stock_extractor import extract_stock_symbols
from pivot_calculator import calculate_pivot_levels
from chart_generator import generate_lightweight_chart
from data_fetcher import fetch_stock_data,previous_day_data,get_security_id
from R3breakout import detect_r3_breakout
from S3breakout import detect_s3_breakdown
from dhanhq import dhanhq
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
client_id = '1100467218'
access_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzU1NjcwOTc3LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMDQ2NzIxOCJ9.j_kLmFQiyykllzsid5e0vQFgaOfVdHUJ5zExAcZ-S_y2sED8ZwXDrKiPpJONxhbn6oie0ytZ9rQNZDUDnH5uZw'
dhan = dhanhq(client_id, access_token)
st.set_page_config(layout="wide")
st.markdown("""
<style>
.stApp { max-width: 100%; }
.main .block-container {
    max-width: 100%;
    padding: 1rem;
}
.stColumn { padding: 0 0.5rem; }
.chart-container {
    width: 100%;
    height: 550px;
    margin-bottom: 2rem;
}
.auto-refresh-info {
    background-color: #f0f2f6;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 20px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)
for key in ["auto_refresh", "last_refresh", "analysis_triggered", "first_run", "breakout_log", "breakdown_log"]:
    if key not in st.session_state:
        st.session_state[key] = {
            "auto_refresh": True,
            "last_refresh": time.time(),
            "analysis_triggered": False,
            "first_run": True,
            "breakout_log": [],
            "breakdown_log": []
        }.get(key)


class StockAnalyzer:
    def process_stock(self, stock: str, stock_type: str) -> dict:
        """Process a single stock and return its analysis results"""
        try:
            # Fetch stock data with more error checking
            stock_data = fetch_stock_data(stock)
            if stock_data is None or stock_data.empty:
                logger.warning(f"No data available for {stock}")
                return None
                
            previous_data = previous_day_data(stock)
            if previous_data is None or previous_data.empty:
                logger.warning(f"No previous day data available for {stock}")
                return None

            # Calculate pivot levels with validation
            try:
                pivot_levels = calculate_pivot_levels(previous_data)
                if not pivot_levels or len(pivot_levels) == 0:
                    logger.warning(f"Invalid pivot levels for {stock}")
                    return None
            except Exception as e:
                logger.error(f"Error calculating pivot levels for {stock}: {str(e)}")
                return None

        # Rest of your processing logic...

            # Perform analysis based on stock type
            if stock_type == "PE":
                breakdown_results, other_results = detect_s3_breakdown(stock_data, pivot_levels, stock_type)
                if breakdown_results is not None and len(breakdown_results) > 0:
                    return {
                        'stock': stock,
                        'type': 'breakdown',
                        'results': breakdown_results,
                        'data': stock_data,
                        'pivot_levels': pivot_levels
                    }
            else:  # CE
                breakout_results = detect_r3_breakout(stock_data, pivot_levels, stock_type)
                if breakout_results is not None and len(breakout_results) > 0:
                    return {
                        'stock': stock,
                        'type': 'breakout',
                        'results': breakout_results,
                        'data': stock_data,
                        'pivot_levels': pivot_levels
                    }
            return None
                
        except Exception as e:
            logger.error(f"Error processing {stock}: {str(e)}")
            return None

def format_timestamp(timestamp):
    """Format timestamp to show complete datetime"""
    try:
        if isinstance(timestamp, str):
            timestamp = pd.to_datetime(timestamp)
        
        # Format to YYYY-MM-DD HH:MM:SS
        return timestamp.strftime('%Y-%m-%d %H:%M:%S')
        
    except Exception as e:
        logger.error(f"Error formatting timestamp: {str(e)}")
        return "Error"

def generate_and_display_charts(stocks, container, analysis_results=None):
    for stock in stocks:
        try:
            data = fetch_stock_data(stock)
            previous_data=previous_day_data(stock)
            if data is None or data.empty or previous_data is None or previous_data.empty:
                container.warning(f"⚠️ Temporarily unavailable: {stock}")
                continue

            
            # Calculate pivot levels
            pivot_levels = calculate_pivot_levels(previous_data)
            # print(data)
            if not data.empty:
                container.subheader(f"📊 {stock}")
                
                # Calculate EMAs
                data['EMA_9'] = data['close'].ewm(span=9, adjust=False).mean()
                data['EMA_15'] = data['close'].ewm(span=15, adjust=False).mean()

                # Prepare data for chart
                df = data[['Date', 'open', 'high', 'low', 'close']].copy()
                df['time'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%dT%H:%M:%S')
                df = df[['time', 'open', 'high', 'low', 'close']]

                # Prepare EMA data
                ema_9 = data.reset_index()[['Date', 'EMA_9']].dropna().copy()
                ema_9.columns = ['time', 'value']
                ema_9['time'] = pd.to_datetime(ema_9['time']).dt.strftime('%Y-%m-%dT%H:%M:%S')

                ema_15 = data.reset_index()[['Date', 'EMA_15']].dropna().copy()
                ema_15.columns = ['time', 'value']
                ema_15['time'] = pd.to_datetime(ema_15['time']).dt.strftime('%Y-%m-%dT%H:%M:%S')

                # Get pivot levels and filter them
                # print(df)
              
  
                with container.expander(f"Pivot Levels for {stock}"):
                    st.write("### Calculated Pivot Levels")
                    for level, value in pivot_levels.items():
                        st.write(f"{level}: {value:.2f}")
                    if not ema_9.empty and not ema_15.empty:
                        latest_ema9 = ema_9.iloc[-1]['value']
                        latest_ema15 = ema_15.iloc[-1]['value']
                        st.write(f"**EMA 9 (Plotted)**: {latest_ema9:.2f}")
                        st.write(f"**EMA 15 (Plotted)**: {latest_ema15:.2f}") 

                # Display analysis results if available
                if analysis_results and stock in [r['stock'] for r in analysis_results]:
                    result = next(r for r in analysis_results if r['stock'] == stock)

                    with container.expander("📈 Analysis Details"):
                        if result['type'] == 'breakdown':
                            st.write(f"Breakdown Price: {result['results'][0]['price']:.2f}")
                            st.write(f"S3 Level: {result['results'][0]['s3_level']:.2f}")
                            breakdown_time = result['results'][0]['datetime']
                            st.write(f"Breakdown Time: {format_timestamp(breakdown_time)}")
                            
                        else:
                            st.write(f"Breakout Price: {result['results'][0]['price']:.2f}")
                            st.write(f"R3 Level: {result['results'][0]['r3_level']:.2f}")
                            breakout_time = result['results'][0]['timestamp']
                            st.write(f"Breakout Time: {format_timestamp(breakout_time)}")
                            


                # Generate and display chart
                chart_code = generate_lightweight_chart(df, ema_9, ema_15,pivot_levels, stock)
                responsive_chart = f"<div class='chart-container'>{chart_code}</div>"
                components.html(responsive_chart, height=550, scrolling=False)
            else:
                container.warning(f"No data found for {stock}")
        except Exception as e:
            container.error(f"Error fetching data for {stock}: {str(e)}")

def fetch_stock_symbols_concurrently(url1, url2):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future1 = executor.submit(extract_stock_symbols, url1)
        future2 = executor.submit(extract_stock_symbols, url2)
        return future1.result(), future2.result()
if "historical_breakouts" not in st.session_state:
    st.session_state.historical_breakouts = {
        "breakouts": {},
        "breakdowns": {},
        "last_updated": None
    }
def place_order_if_not_placed(stock, type_):
    """Place order using Dhan API only if not already placed."""
    log_file = "orders_log.csv"
    today = datetime.now().strftime('%Y-%m-%d')
    security_id = get_security_id(stock)

    # Load log if exists
    if os.path.exists(log_file):
        order_log = pd.read_csv(log_file)
    else:
        order_log = pd.DataFrame(columns=["Date", "Stock", "Type"])

    # Check if order for this stock and type is already placed today
    already_placed = (
        (order_log["Date"] == today) &
        (order_log["Stock"] == stock) &
        (order_log["Type"] == type_)
    ).any()

    if already_placed:
        logger.info(f"🔁 Order already placed today for {stock} ({type_})")
        return

    try:
        # Place the order - update `security_id`, quantity, etc.
        dhan.place_order(
            security_id=security_id,  # You should map stock symbol to its actual ID
            exchange_segment=dhan.NSE,
            transaction_type=dhan.BUY,
            quantity=1,
            order_type=dhan.MARKET,
            product_type=dhan.INTRA,
            price=0
        )
        logger.info(f"✅ Order placed for {stock} ({type_})")

        # Log the order
        new_entry = pd.DataFrame([{
            "Date": today,
            "Stock": stock,
            "Type": type_
        }])
        order_log = pd.concat([order_log, new_entry], ignore_index=True)
        order_log.to_csv(log_file, index=False)

    except Exception as e:
        logger.error(f"❌ Failed to place order for {stock}: {str(e)}")
def display_historical_breakouts():
    st.sidebar.subheader("📅 Historical Signals Today")
    
    # Show breakouts
    if st.session_state.historical_breakouts["breakouts"]:
        st.sidebar.markdown("### 🔺 Breakouts (CE)")
        for stock, data in st.session_state.historical_breakouts["breakouts"].items():
            delta = datetime.now() - data["first_detected"]
            st.sidebar.markdown(
                f"""
                **{stock}**  
                🕒 First detected: {delta.seconds//60} minutes ago  
                🔄 Last seen: {(datetime.now() - data['last_detected']).seconds//60} min ago  
                💰 Breakout Price: {data['details']['results'][0]['price']:.2f}  
                📈 R3 Level: {data['details']['results'][0]['r3_level']:.2f}
                """
            )
    else:
        st.sidebar.info("No breakouts detected yet today")
    
    # Show breakdowns
    if st.session_state.historical_breakouts["breakdowns"]:
        st.sidebar.markdown("### 🔻 Breakdowns (PE)")
        for stock, data in st.session_state.historical_breakouts["breakdowns"].items():
            delta = datetime.now() - data["first_detected"]
            st.sidebar.markdown(
                f"""
                **{stock}**  
                🕒 First detected: {delta.seconds//60} minutes ago  
                🔄 Last seen: {(datetime.now() - data['last_detected']).seconds//60} min ago  
                💰 Breakdown Price: {data['details']['results'][0]['price']:.2f}  
                📉 S3 Level: {data['details']['results'][0]['s3_level']:.2f}
                """
            )
    else:
        st.sidebar.info("No breakdowns detected yet today")
def append_to_excel_breakout(detected_result):
    # Extract useful info
    stock = detected_result['stock']
    type_ = detected_result['type']
    result_data = detected_result['results'][0]
    price = result_data['price']
    level = result_data.get('r3_level') if type_ == 'breakout' else result_data.get('s3_level')
    timestamp = result_data.get('timestamp') or result_data.get('datetime')

    # Prepare the row
    row = {
        'Stock': stock,
        'Type': type_,
        'Price': price,
        'Level': level,
        'Timestamp': timestamp,
        'Detected At': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    # Excel file path
    date_str = datetime.now().strftime('%Y-%m-%d')
    filename = f"breakout_log_{date_str}.xlsx"

    try:
        # Load existing or create new
        try:
            existing_df = pd.read_excel(filename)
            df = pd.concat([existing_df, pd.DataFrame([row])], ignore_index=True)
        except FileNotFoundError:
            df = pd.DataFrame([row])

        # Save
        df.to_excel(filename, index=False)

    except Exception as e:
        logger.error(f"Error writing to Excel file: {e}")
import os

def append_to_excel(detected_result):
    # Extract data
    stock = detected_result['stock']
    type_ = detected_result['type']
    result_data = detected_result['results'][0]
    price = result_data['price']
    level = result_data.get('r3_level') if type_ == 'breakout' else result_data.get('s3_level')
    timestamp = result_data.get('timestamp') or result_data.get('datetime')

    # Format row
    new_row = {
        'Stock': stock,
        'Type': type_,
        'Price': price,
        'Level': level,
        'Timestamp': format_timestamp(timestamp)
    }

    # File path
    date_str = datetime.now().strftime('%Y-%m-%d')
    filename = f"breakout_log_{date_str}.csv"

    try:
        # If file exists, load and check for duplicate
        if os.path.exists(filename):
            existing_df = pd.read_csv(filename)
            duplicate = (
                (existing_df['Stock'] == stock) & 
                (existing_df['Type'] == type_)
            ).any()

            if duplicate:
                logger.info(f"Duplicate entry skipped: {stock} ({type_})")
                return  # Skip adding

            df = pd.concat([existing_df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            df = pd.DataFrame([new_row])

        # Write the result
        df.to_csv(filename, index=False)
        logger.info(f"✅ Logged: {stock} ({type_})")

    except Exception as e:
        logger.error(f"Error writing to CSV: {e}")




def run_analysis():
    """Main analysis function that will be called automatically"""
    # URLs for PE and CE stocks
    chartink_url1 = "https://chartink.com/screener/sell-f-o-stocks-futures"
    chartink_url2 = "https://chartink.com/screener/fno-stocks-buy-76"

    with st.spinner("🔄 Fetching and analyzing stocks..."):
        # Fetch stocks
        pe_stocks, ce_stocks = fetch_stock_symbols_concurrently(chartink_url1, chartink_url2)
        st.success(f"📊 Found {len(pe_stocks)} PE stocks and {len(ce_stocks)} CE stocks")

        # Initialize analyzer and process stocks
        analyzer = StockAnalyzer()
        breakdown_results = []
        breakout_results = []

        # Process stocks with progress bar
        progress_bar = st.progress(0)
        total_stocks = len(pe_stocks) + len(ce_stocks)
        processed = 0

        # Process PE stocks
        for stock in pe_stocks:
            result = analyzer.process_stock(stock, "PE")
            if result:
                breakdown_results.append(result)
            processed += 1
            progress_bar.progress(processed / total_stocks)

        # Process CE stocks
        for stock in ce_stocks:
            result = analyzer.process_stock(stock, "CE")
            if result:

                breakout_results.append(result)
            processed += 1
            progress_bar.progress(processed / total_stocks)
        current_time = datetime.now()
        for result in breakout_results:
            stock = result['stock']
            if stock not in st.session_state.historical_breakouts["breakouts"]:
                append_to_excel(result)
                st.session_state.historical_breakouts["breakouts"][stock] = {
                    "first_detected": current_time,
                    "last_detected": current_time,
                    "details": result
                }
                # place_order_if_not_placed(stock, "breakout")

            else:
                st.session_state.historical_breakouts["breakouts"][stock]["last_detected"] = current_time
        for result in breakdown_results:
            stock = result['stock']
            if stock not in st.session_state.historical_breakouts["breakdowns"]:
                append_to_excel(result)
                st.session_state.historical_breakouts["breakdowns"][stock] = {
                    "first_detected": current_time,
                    "last_detected": current_time,
                    "details": result
                }
            else:
                st.session_state.historical_breakouts["breakdowns"][stock]["last_detected"] = current_time
        progress_bar.empty()

        # Display results in columns
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🔻 Downward Momentum Stocks (PE)")
            if breakdown_results:
                generate_and_display_charts([r['stock'] for r in breakdown_results], col1, breakdown_results)
            else:
                st.info("No breakdown patterns found. Showing all PE stocks:")
                generate_and_display_charts(pe_stocks, col1)

        with col2:
            st.subheader("🔺 Upward Momentum Stocks (CE)")
            if breakout_results:
                generate_and_display_charts([r['stock'] for r in breakout_results], col2, breakout_results)
            else:
                st.info("No breakout patterns found. Showing all CE stocks:")
                generate_and_display_charts(ce_stocks, col2)


        # Display summary in sidebar
        st.sidebar.success(f"""
        ### 📊 Analysis Summary
        - Total Stocks Analyzed: {total_stocks}
        - Breakdown Patterns Found: {len(breakdown_results)}
        - Breakout Patterns Found: {len(breakout_results)}
        """)
        display_historical_breakouts()

# Initialize session state
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True  # Start with auto-refresh enabled
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()
if 'analysis_triggered' not in st.session_state:
    st.session_state.analysis_triggered = False
if 'first_run' not in st.session_state:
    st.session_state.first_run = True  # Track if this is the first run

# Main execution
st.markdown("<h1 style='text-align: center'>Stock Analysis Dashboard</h1>", unsafe_allow_html=True)

# Auto-refresh controls
col_left, col_center, col_right = st.columns([1, 2, 1])

with col_center:
    auto_refresh_enabled = st.checkbox("🔄 Enable Auto-Refresh (Every 1 minute)", value=st.session_state.auto_refresh)
    st.session_state.auto_refresh = auto_refresh_enabled

# Display auto-refresh status and handle timing
current_time = time.time()
time_since_refresh = int(current_time - st.session_state.last_refresh)

if st.session_state.auto_refresh:
    next_refresh_in = max(0, 60 - time_since_refresh)
    
    st.markdown(f"""
    <div class='auto-refresh-info'>
        ✅ Auto-refresh is ENABLED | Next refresh in: <strong>{next_refresh_in}</strong> seconds
        <br>Last updated: {datetime.fromtimestamp(st.session_state.last_refresh).strftime('%H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)
    
    # Auto-refresh logic - trigger analysis when time is up
    if time_since_refresh >= 60:
        st.session_state.last_refresh = current_time
        st.session_state.analysis_triggered = True
        st.rerun()

# Add custom button styling
st.markdown("""
<style>
div.stButton > button {
    display: block;
    margin: 0 auto;
    font-size: 24px;
    padding: 10px 20px;
    width: 200px;
    color: green;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# Manual analysis button
manual_trigger = st.button("🔄 Force Refresh Now")

# Run analysis on first load, when manually triggered, or auto-refresh triggered
if st.session_state.first_run or manual_trigger or st.session_state.analysis_triggered:
    if manual_trigger:
        st.session_state.last_refresh = current_time
    
    # Reset triggers
    st.session_state.analysis_triggered = False
    st.session_state.first_run = False
    
    # Run the analysis
    run_analysis()

# Continuous refresh mechanism for auto-refresh mode
if st.session_state.auto_refresh:
    # Use meta refresh for reliable auto-refresh
    refresh_interval = max(1, 61 - time_since_refresh)  # Refresh slightly after 60 seconds
    st.markdown(f"""
    <meta http-equiv="refresh" content="{refresh_interval}">
    <script>
    // Backup JavaScript refresh
    setTimeout(function(){{
        window.location.reload(1);
    }}, {refresh_interval * 1000});
    </script>
    """, unsafe_allow_html=True)