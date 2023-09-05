import pandas as pd
import json
from datetime import datetime, timedelta
import numpy as np

def calculate_metrics(stocks_data, years=0): 

    dict_dataframes = {}

    tickers = stocks_data.columns.to_list()
    index_symbol = tickers.pop()
    # print(tickers,"\n",index_symbol)

    if years > 0: # 0 is the default value. If that value is received, use the entire data set 
        # We'll need to slice the price data and get latest {years} number of years data 
        # Calculate the start and end dates for the past 5 years
        end_date = datetime.today().date()
        start_date = end_date - timedelta(days=years*365)
        print(f"Running calculate_metrics on period: {start_date} to {end_date}")
        price_data = stocks_data.loc[start_date : end_date]
    else: 
        price_data = stocks_data.copy()

    #Calculate daily change stocks
    dict_dataframes['combined_returns'] = price_data.pct_change()       # .dropna() - Removing this because some of the tickers dont have data for 10 yrs. 
                                                                        # This was dropping valid prices too
    dict_dataframes['combined_returns'] = dict_dataframes['combined_returns'].iloc[1:]
    # We will just fillnas with 0
    dict_dataframes['combined_returns'] = dict_dataframes['combined_returns'].fillna(0)
    # print(dict_dataframes['combined_returns'].isna().sum())

    dict_dataframes['cum_returns'] = (1 + dict_dataframes['combined_returns']).cumprod(axis=0)

    dict_dataframes['cum_returns_sma'] = dict_dataframes['cum_returns'].rolling(window=180).mean().dropna()
    dict_dataframes['cum_returns_std'] = dict_dataframes['cum_returns'].rolling(window=180).std().dropna()
    dict_dataframes['volatility'] = dict_dataframes['combined_returns'].std() * np.sqrt(252)
    dict_dataframes['returns_variance'] = dict_dataframes['combined_returns'].var()
    dict_dataframes['cov_matrix'] = dict_dataframes['combined_returns'].cov()

    df = pd.concat([dict_dataframes['volatility'], dict_dataframes['returns_variance'], dict_dataframes['cov_matrix'][index_symbol]], axis="columns")
    df.columns = ['Volatility', 'Variance', 'Covariance']

    # Code to calculate Beta
    #Find variance of the Index ticker
    variance_of_index = dict_dataframes['combined_returns'].iloc[:,-1].var()

    df['Beta'] = df['Covariance'] / variance_of_index

    df = pd.concat([df, pd.Series(dict_dataframes['combined_returns'].mean() * 252 /  dict_dataframes['volatility'], name="Sharpe_Ratio")], axis='columns')
    dict_dataframes["df_metrics"] = df

    return dict_dataframes