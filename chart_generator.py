import logging
from lightweight_charts import Chart
import pandas as pd
from datetime import datetime
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
# import concurrent.futures




# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import json
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

# Function to generate Lightweight Chart HTML
def generate_lightweight_chart(df, ema_9, ema_15, pivot_levels, stock_symbol):
    try:
        # Prepare candlestick data
        df['time'] = pd.to_datetime(df['time']).apply(lambda x: int(x.timestamp()))
        candlestick_series_data = df[['time', 'open', 'high', 'low', 'close']].to_dict(orient='records')
        # print(candlestick_series_data)
        
        # print(json.dumps(candlestick_series_data, indent=2))
        ema_15['time'] = pd.to_datetime(ema_15['time']).apply(lambda x: int(x.timestamp()))
        ema_9['time'] = pd.to_datetime(ema_9['time']).apply(lambda x: int(x.timestamp()))
        

        ema_9_data = ema_9[['time', 'value']].to_dict(orient='records')
        ema_15_data = ema_15[['time', 'value']].to_dict(orient='records')
        # print("ema_15",ema_15_data,"ema_9",ema_9_data)
    #     chart=Chart()
    #     chart.set(candlestick_series_data)

    # # add sma line
    #     line = chart.create_line()    
    #     line.set(ema_9_data)
    #     line.set(ema_15_data)
        
    #     chart.show(block=True)

        
        # Prepare Pivot Levels
        # pivot_levels = json.dumps(pivot_levels)

        # Create HTML code for the chart
        chart_code = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Stock Chart - {stock_symbol}</title>
            <script src="https://unpkg.com/lightweight-charts@3.8.0/dist/lightweight-charts.standalone.production.js"></script>
        </head>
        <body>
            <div id="chart" style="width: 100%; height: 500px;"></div>
            <script>
                const chart = LightweightCharts.createChart(document.getElementById('chart'), {{
                    width: window.innerWidth * 0.9,
                    height: 500,
                    layout: {{
                        backgroundColor: '#ffffff',
                        textColor: '#000000',
                    }},
                    grid: {{
                        vertLines: {{ color: '#e0e0e0' }},
                        horzLines: {{ color: '#e0e0e0' }},
                    }},
                    timeScale: {{
                        timeVisible: true,
                        borderColor: '#cccccc',
                        
                    }},
                }});
            
                // Add candlestick series
                const candlestickSeries = chart.addCandlestickSeries({{
                    upColor: '#26a69a',
                    downColor: '#ef5350',
                    borderVisible: false,
                    wickUpColor: '#26a69a',
                    wickDownColor: '#ef5350',
                }});
                candlestickSeries.setData({json.dumps(candlestick_series_data,indent=2)});


                // Add EMA 9 series
                const ema9Series = chart.addLineSeries({{
                    color: '#3236a8',
                    lineWidth: 2,
                }});
                ema9Series.setData({json.dumps(ema_9_data)});

                // Add EMA 15 series
                const ema15Series = chart.addLineSeries({{
                    color: '#32a852',
                    lineWidth: 2,
                }});
                ema15Series.setData({json.dumps(ema_15_data)});

                // Add pivot levels
                const pivotLevels = {pivot_levels};
                const pivotColors = {{
                    'r1': '#FF0000', 's1': '#32CD32','r2':'#CD3292','r3': '#FFA500','r4':'#870B4D','r5':'#FF69B4','s2':'#008000','s3': '#006400','s4':'#000800','s5':'#4B0082'
                }};
                

                Object.keys(pivotLevels).forEach(level => {{
                    chart.addLineSeries({{
                        text: 'r1',
                        color: pivotColors[level],
                        lineWidth: 1,
                    }}).setData([
                        {{ time: {df['time'].min()}, value: pivotLevels[level] }},
                        {{ time: {df['time'].max()}, value: pivotLevels[level] }}
                    ]);
                    
                }});

                // Resize chart dynamically
                window.addEventListener('resize', () => {{
                    chart.resize(window.innerWidth * 0.9, 500);
                }});
            </script>
        </body>
        </html>
        """
        return chart_code
    except Exception as e:
        return f"<div>Error generating chart: {str(e)}</div>"
