# 📈 Live Stock Screener & Trade Execution System

A real-time stock screening and auto-trading platform built with **Python**, **Streamlit**, and **Dhan API**. It uses **Chartink** filters (EMA-9/EMA-15 crossover), generates **1-min candlestick charts** via **TradingView**, and places live trades for shortlisted stocks through Dhan's API.

---

## 🎥 Demo Video

[![Watch Demo](https://img.shields.io/badge/Watch-Demo-blue?logo=youtube)](https://drive.google.com/file/d/13_TokRslmJLDR2cNBBZ-ky9T5s3Eiwuy/view?usp=sharing)

---

## 🚀 Features

- 🔍 **Chartink Integration**  
  Fetches live stock symbols based on EMA-9/EMA-15 crossover filter logic.

- 📊 **Live Market Data**  
  Uses Dhan API to fetch 1-minute candlestick data for real-time visualization.

- 📈 **Candlestick Charting**  
  Charts rendered using TradingView API, with pivot and support/resistance overlays.

- 🎯 **Pivot Breakout Strategy**  
  Calculates Camarilla pivot points; highlights stocks breaking R3 for potential entries.

- 🧠 **Strategy Filter**  
  Only displays charts meeting technical conditions (momentum + breakout).

- 💼 **Auto Trade Execution**  
  Automatically places buy orders for shortlisted stocks via Dhan API.

- 🌐 **Interactive Dashboard**  
  Built with Streamlit — fully interactive and auto-refreshing chart panel.

---

## 🧰 Tech Stack

- **Frontend**: Streamlit, TradingView Chart API  
- **Backend**: Python, Pandas, Chartink Scraper, Camarilla Logic  
- **Data API**: Dhan API (Market Feed + Order Placement)  
- **Automation**: Schedule / Refresh via Streamlit  

📬 Contact
Aryan Verma
📧 Email: aryan04.av@gmail.com

⚠️ Disclaimer
This project is for educational and demo purposes only. Do not use it for live trading without proper risk management and backtesting.

