import pandas as pd
import logging
from datetime import time

logger = logging.getLogger(__name__)

def detect_r3_breakout(df, pivot_levels, stock_type="CE", debug=False):

    """
    Detect R3 breakout patterns in stock data
    Returns list of breakout patterns found
    """
    try:
        if debug:
            logger.debug(f"Starting R3 breakout detection")
            logger.debug(f"First timestamp in data: {df.index[0]}")

        breakout_stocks = []
        other_stocks = []
        confirmation_count = 0
        confirmation_needed = 2
        breakout_start_time = None

        r3_level = pivot_levels.get('r3')
        if r3_level is None:
            logger.error("R3 level not found in pivot levels")
            return None
        # Ensure index is datetime
        df.index = pd.to_datetime(df.index)

        for idx in df.index:
            candle = df.loc[idx]
            current_price = candle['close']
            
            if current_price > r3_level:
                if confirmation_count == 0:
                    breakout_start_time = idx  # Store the first breakout candle time
                confirmation_count += 1
                
                if confirmation_count >= confirmation_needed:
                    breakout_stocks.append({
                        'type': 'CE Breakout',
                        'timestamp': df.loc[idx, 'Date'],  # Use the initial breakout time
                        'price': current_price,
                        'r3_level': r3_level,
                        'breakout_percentage': ((current_price - r3_level) / r3_level) * 100
                    })
                    if debug:
                        logger.debug(f"Breakout found at timestamp: {breakout_start_time}")
                    break
            else:
                confirmation_count = 0
                breakout_start_time = None

        return breakout_stocks + other_stocks

    except Exception as e:
        logger.error(f"Error in detect_r3_breakout: {str(e)}", exc_info=True)
        return None