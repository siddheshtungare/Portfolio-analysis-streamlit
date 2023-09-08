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
from UtilFuncs.calculations import * 

# Read the json file containing the tickers corresponding to the index
with open('Resources/symbols_list.json', 'r') as json_file:
    symbols_dict = json.load(json_file)

# start the streamlit app and show a multiselect widget to select the tickers
st.set_page_config(
        page_title="Portfolio Optimization",
        layout="wide"
    )

st.title("Portfolio Optimization")

# First section of app - this is for the user to select the tickers, and the index they want to run it for
index_symbol = [st.selectbox("Select index", ['^AXJO'])]  # 'NDX',  @ToDo: More work needed for the Nasdaq listed securities

st.write("Please select the tickers you want to include in your portfolio")
tickers_with_name = st.multiselect("Select tickers", symbols_dict[index_symbol[0]], placeholder="Choose an option", max_selections=10)
tickers = [ticker.split(":")[0] for ticker in tickers_with_name]

st.write(f"You selected the following index: {index_symbol[0]}")    
st.write(f"You selected the following tickers: {tickers}")  

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

        computed_results = calculate_metrics(stock_data)
        combined_returns = computed_results['combined_returns']
        cum_returns = computed_results['cum_returns']
        cum_returns_sma = computed_results['cum_returns_sma']
        cum_returns_std = computed_results['cum_returns_std']
        volatility = computed_results['volatility']
        returns_variance = computed_results['returns_variance']
        cov_matrix = computed_results['cov_matrix']
        df_metrics = computed_results['df_metrics']

        # Sharpe Ratios
        # sharpe_ratios = (combined_returns.mean() * 252) / volatility

        tab0, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["DataFrames", "Returns", "Standard Dev. and Volatility", \
                                                      "Risk Analysis", "Efficient Frontier", "Recommendations", "Fundamentals"])

        # This is only for dev analysis. We can print out the dataframes in this tab 
        with tab0: 
            # Row1: 
            st.header("Only for development analysis. Need to comment out this tab later")

            st.markdown("**Printing out all Dataframes used in this app**")
            st.write("combined_returns")
            st.dataframe(combined_returns)
            st.write("cum_returns")
            st.dataframe(cum_returns)
            st.write("cum_returns_sma")
            st.dataframe(cum_returns_sma)
            st.write("cum_returns_std")
            st.dataframe(cum_returns_std)
            st.write("volatility")
            st.dataframe(volatility)
            st.write("returns_variance")
            st.dataframe(returns_variance)
            st.write("cov_matrix")
            st.dataframe(cov_matrix)
            st.write("dataframe_concatenated")
            st.dataframe(df_metrics)

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
                fig7 = px.bar(df_metrics['Beta'], x=df_metrics.index, y='Beta', title=f"Beta score with ref to {index_symbol[0]}")
                st.plotly_chart(fig7)

            with col_3_4:
                fig8 = px.bar(df_metrics['Sharpe_Ratio'], title="Sharpe Ratios")   
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

        # Tab5: Recommendations
        with tab5: 
            st.header("Efficient Frontier - on Recommended Tickers")

            df_prices_top_20 = pd.read_csv("Resources/Recommendations_top_20_prices.csv", index_col=0, parse_dates=True, infer_datetime_format=True)

            # Taking last 5 years data 
            ef_outcomes_top_20 = run_ef_with_random(df_prices_top_20.iloc[1265:].copy())

            # Row1: to show EF plot and outcomes 
            col_5_1, col_5_2 = st.columns([0.6, 0.4])

            with col_5_1:
                st.plotly_chart(ef_outcomes_top_20[1])

            with col_5_2:
                st.markdown(ef_outcomes_top_20[0])

        # Tab6: Fundamental Analysis
        with tab6: 
            st.header("Fundamental Analysis of your stocks")

            df_fundamentals = pd.read_csv(f"Resources/Fundamentals_data_{index_symbol[0]}.csv", index_col=0)

            # Row1: to show histograms 
            col_6_1, col_6_2 = st.columns(2)

            with col_6_1:
                fig1 = px.histogram(df_fundamentals, y="marketCap", hover_data=df_fundamentals.columns)
                st.plotly_chart(fig1)
                # st.dataframe(df_fundamentals)

            with col_6_2:
                st.markdown("### Coming Soon")



