import pandas as pd
import logging
from datetime import time

logger = logging.getLogger(__name__)

def detect_s3_breakdown(df, pivot_levels, stock_type="PE", debug=False):
    """
    Detect S3 breakdown patterns in stock data
    Returns two lists: confirmed breakdowns and other patterns
    """
    try:
        if debug:
            logger.debug(f"Starting S3 breakdown detection")
            logger.debug(f"First timestamp in data: {df.index[0]}")

        breakdown_stocks = []
        other_stocks = []
        confirmation_count = 0
        confirmation_needed = 2
        breakdown_start_time = None
        s3_level = pivot_levels.get('s3')
        if s3_level is None:
            logger.error("S3 level not found in pivot levels")
            return None, None

        # Ensure index is datetime
        df.index = pd.to_datetime(df.index)

        for idx in df.index:
            candle = df.loc[idx]
            current_price = candle['close']
            
            if current_price < s3_level:
                if confirmation_count == 0:
                    breakdown_start_time = idx  # Store the first breakdown candle time
                confirmation_count += 1
                
                if confirmation_count >= confirmation_needed:
                    breakdown_stocks.append({
                        'type': 'PE Breakdown',
                        'datetime': df.loc[idx, 'Date'],  # Use the initial breakdown time
                        'price': current_price,
                        's3_level': s3_level,
                        'breakdown_percentage': ((s3_level - current_price) / s3_level) * 100
                    })
                    if debug:
                        logger.debug(f"Breakdown found at timestamp: {breakdown_start_time}")
                    break
            else:
                confirmation_count = 0
                breakdown_start_time = None

        return breakdown_stocks, other_stocks

    except Exception as e:
        logger.error(f"Error in detect_s3_breakdown: {str(e)}", exc_info=True)
        return None, None