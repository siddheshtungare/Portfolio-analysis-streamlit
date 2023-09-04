import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_securities_prices(tickers, num_years=10): 

    # Calculate the start and end dates for the past 5 years
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=num_years*365)  

    # ================================Historical data of Securities=====================================

    # Fetch historical price data
    stock_data = yf.download(tickers, start=start_date, end=end_date)

    #Drop Nulls. Remove high, low, open data. 
    stock_data = stock_data.drop(columns=['Open', 'Volume', 'Close', 'High', 'Low'])

    stock_data.columns = stock_data.columns.droplevel(0) if len(tickers) > 1 else tickers

    # ================================US Treasury Bonds data=============================================
    # Fetch Risk Free rate using US10 Treasury Bond
    # Fetch historical price data
    us10_data = yf.download("^TNX", start=start_date, end=end_date)

    #Drop Nulls. Remove high, low, open data. 
    us10_data = us10_data.drop(columns=['Open', 'Volume', 'Close', 'High', 'Low'])

    return stock_data,  us10_data