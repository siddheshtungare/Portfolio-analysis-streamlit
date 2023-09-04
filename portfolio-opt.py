#Imports
import pandas as pd
import json
from datetime import datetime, timedelta
import hvplot.pandas
import numpy as np
import pypfopt
import matplotlib.pyplot as plt
from pypfopt.expected_returns import mean_historical_return
from pypfopt import plotting
from pypfopt.risk_models import risk_matrix
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import objective_functions
import scipy.optimize as sco
import streamlit as st 
import plotly.express  as px
import plotly.graph_objects as go
import chart_studio.plotly as py

from UtilFuncs.get_yfinance_data import * 
from UtilFuncs.visualizations_1 import *

with open('Resources/symbols_list.json', 'r') as json_file:
    symbols_dict = json.load(json_file)

# start the streamlit app and show a multiselect widget to select the tickers
st.set_page_config(
        page_title="Portfolio Optimization",
        layout="wide"
    )

st.title("Portfolio Optimization")

# First section of st - this is for the user to select the tickers, and the index they want to run it for

index_symbol = [st.selectbox("Select index", ['^AXJO'])]  # 'NDX',  @ToDo: More work needed for the Nasdaq listed securities

st.write("Please select the tickers you want to include in your portfolio")
tickers_with_name = st.multiselect("Select tickers", symbols_dict[index_symbol[0]], placeholder="Choose an option", max_selections=10)
tickers = [ticker.split(":")[0] for ticker in tickers_with_name]

st.write(f"You selected the following tickers: {tickers}")  

st.write(f"You selected the following index: {index_symbol[0]}")    

stock_data, us10_data = get_securities_prices(tickers + index_symbol, num_years = 5)

#Calculate daily change stocks
combined_returns = stock_data.pct_change().dropna()
#Calculate daily change 10yr treasury
us10_daily_change = us10_data.pct_change().dropna()

if len(tickers) > 0 and len(index_symbol) > 0: 

    run_visuals = st.button("Show Visualizations on ticker prices")
    # st.dataframe(stock_data.iloc[:10], use_container_width=True)

    if run_visuals: 

        # Compute all the necessary dataframes/values that we will need to show our Visualizations
        cum_returns = (1 + combined_returns).cumprod(axis=0)
        cum_returns_sma = cum_returns.rolling(window=180).mean().dropna()
        cum_returns_std = cum_returns.rolling(window=180).std().dropna()
        volatility = combined_returns.std() * np.sqrt(252)
        returns_variance = combined_returns.var()
        cov_matrix = combined_returns.cov()

        # Code to calculate Beta
        #Find variance of the Index ticker
        variance_of_index = combined_returns[index_symbol[0]].var()
        # Create an empty DataFrame to store beta values
        beta_df = pd.DataFrame(columns=['Ticker', 'Beta'])
        # Iterate through the tickers, use the covariance against index and calculate beta
        for i, ticker in enumerate(tickers):
            cov = cov_matrix[ticker][index_symbol].item()
            beta = cov / variance_of_index
            beta_df = beta_df.append({'Ticker': ticker, 'Beta': beta}, ignore_index=True)
        beta_df.set_index('Ticker',inplace=True)
        beta_df.sort_index(inplace=True)

        # Sharpe Ratios
        sharpe_ratios = (combined_returns.mean() * 252) / volatility


        tab1, tab2, tab3, tab4 = st.tabs(["Returns", "Standard Dev. and Volatility", "Risk Analysis", "Efficient Frontier"])

        with tab1: 
            # Row1: Line charts on prices and returns 
            st.header("Line charts on prices and returns")
            
            col_1_1, col_1_2 = st.columns(2)

            with col_1_1:
                fig1 = px.line(cum_returns, title="Returns")
                st.plotly_chart(fig1)

            with col_1_2:
                fig2 = px.line(cum_returns_sma, title="Returns - SMA 180 days")
                st.plotly_chart(fig2)

        # Tab2: Tab for STD and Volatility 
        with tab2:
            st.header("Standard Deviation and Volatility")

            col_2_1, col_2_2 = st.columns(2)

            with col_2_1:
                fig3 = px.line(cum_returns_std, title="Rolling 180 days Standard Deviation")
                st.plotly_chart(fig3)

            with col_2_2:
                fig4 = px.bar(volatility, title="Volatility")
                st.plotly_chart(fig4)

        # Tab3: Tab for Covariance Matrix and Betas
        with tab3:
            st.header("Covariance Matrix, Variance, Beta Score and Sharpe Ratios")

            # Row1: to show Covariance and Variance 
            col_3_1, col_3_2 = st.columns(2)

            with col_3_1:
                fig5 = px.imshow(cov_matrix, text_auto=True, title="Covariance Matrix")
                st.plotly_chart(fig5)

            with col_3_2:
                fig6 = px.bar(returns_variance, title="Variance")
                st.plotly_chart(fig6)


            # Row2: to show Beta and Sharpe Ratios 
            col_3_3, col_3_4 = st.columns(2)

            with col_3_3:
                fig7 = px.bar(beta_df, x=beta_df.index, y='Beta', title=f"Beta score with ref to {index_symbol[0]}")
                st.plotly_chart(fig7)

            with col_3_4:
                fig8 = px.bar(sharpe_ratios, title="Sharpe Ratios")   #, x='Ticker', y='Beta'
                st.plotly_chart(fig8)


        # Tab4: Efficient Frontier
        with tab4: 
            st.header("Efficient Frontier")

            ef_outcomes = run_ef_with_random(stock_data.iloc[:,:-1].copy())

            # Row1: to show EF plot and outcomes 
            col_4_1, col_4_2 = st.columns([0.6, 0.4])

            with col_4_1:
                st.plotly_chart(ef_outcomes[1])

            with col_4_2:
                st.markdown(ef_outcomes[0])


