import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse
import time

def extract_stock_symbols(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    stock_symbols = set()
    try:
        driver.get(url)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'run_scan_button')]"))
        )
        run_scan_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'run_scan_button')]"))
        )
        run_scan_button.click()
        
        time.sleep(10)  # Wait for scan to complete
        
        stock_links = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, 'symbol=')]"))
        )
        for link in stock_links:
            href = link.get_attribute("href")
            symbol = href.split("symbol=")[-1]
            decoded_symbol = urllib.parse.unquote(symbol)
            stock_symbols.add(decoded_symbol + "")  # Add .NS for Yahoo Finance
    except Exception as e:
        st.error(f"Error in stock extraction: {str(e)}")
    finally:
        driver.quit()
    return list(stock_symbols)