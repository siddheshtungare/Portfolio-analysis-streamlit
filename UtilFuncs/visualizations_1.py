#Imports
import pandas as pd
from datetime import datetime, timedelta
# import hvplot.pandas
import numpy as np
import pypfopt
import matplotlib.pyplot as plt
from pypfopt.expected_returns import mean_historical_return
from pypfopt import plotting
from pypfopt.risk_models import risk_matrix
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import objective_functions
import streamlit as st 
import plotly.express  as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import chart_studio.plotly as py

# initialize random seed to generate pseudorandom numbers
np.random.seed()

def portfolio_annualised_performance(weights, mean_returns, cov_matrix):
    returns = np.sum(mean_returns*weights) * 252
    std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
    return std, returns

def random_portfolios(num_portfolios, mean_returns, cov_matrix, risk_free_rate):
    ticker_count = len(mean_returns.to_list())
    results = np.zeros((ticker_count,num_portfolios))
    weights_record = []
    for i in range(num_portfolios):
        weights = np.random.random(ticker_count)
        weights /= np.sum(weights)
        weights_record.append(weights)
        portfolio_std_dev, portfolio_return = portfolio_annualised_performance(weights, mean_returns, cov_matrix)
        results[0,i] = portfolio_std_dev
        results[1,i] = portfolio_return
        results[2,i] = (portfolio_return - risk_free_rate) / portfolio_std_dev
    return results, weights_record



def display_simulated_ef_with_random(stock_data, mean_returns, cov_matrix, num_portfolios, risk_free_rate):
    results, weights = random_portfolios(num_portfolios,mean_returns, cov_matrix, risk_free_rate)
    
    max_sharpe_idx = np.argmax(results[2])
    sdp, rp = results[0,max_sharpe_idx], results[1,max_sharpe_idx]
    max_sharpe_allocation = pd.DataFrame(weights[max_sharpe_idx], index=stock_data.columns,columns=['allocation'])
    max_sharpe_allocation.allocation = [round(i*100,2)for i in max_sharpe_allocation.allocation]
    max_sharpe_allocation = max_sharpe_allocation.T
    
    min_vol_idx = np.argmin(results[0])
    sdp_min, rp_min = results[0,min_vol_idx], results[1,min_vol_idx]
    min_vol_allocation = pd.DataFrame(weights[min_vol_idx],index=stock_data.columns,columns=['allocation'])
    min_vol_allocation.allocation = [round(i*100,2)for i in min_vol_allocation.allocation]
    min_vol_allocation = min_vol_allocation.T
    
    markdown_str = "### Efficient Frontier Portfolio Optimisation \n\n"
    markdown_str += "#### Maximum Sharpe Ratio Portfolio Allocation \n\n"
    markdown_str += f"* Annualised Return: {round(rp,2)}\n\n"
    markdown_str += f"* Annualised Volatility: {round(sdp,2)}\n\n"
    markdown_str += max_sharpe_allocation.to_markdown() + "\n\n"
    markdown_str += "---\n\n"

    markdown_str += "#### Minimum Volatility Portfolio Allocation\n\n"
    markdown_str += f"* Annualised Return: {round(rp_min,2)} \n\n"
    markdown_str += f"* Annualised Volatility: {round(sdp_min,2)} \n\n"
    markdown_str += min_vol_allocation.to_markdown() + "\n\n"

    fig = go.Figure()

    # Add scatter trace with medium sized markers
    fig.add_trace( go.Scatter(mode='markers', x=results[0,:], y=results[1,:], marker=dict( color='LightSkyBlue', size=4, opacity=0.5, 
                        line=dict( color='LightSkyBlue', width=2 ) ), showlegend=False ) )

    fig.add_trace( go.Scatter( mode='markers', x=[sdp], y=[rp], marker=dict( color='Green', size=20, opacity=0.8, 
                        line=dict( color='Green', width=8 ) ), showlegend=True, name="Maximum Sharpe Ratio" ) )

    fig.add_trace( go.Scatter( mode='markers', x=[sdp_min], y=[rp_min], marker=dict( color='Yellow', size=20, opacity=0.8, 
                        line=dict( color='Yellow', width=8 ) ), showlegend=True, name="Minimum Volatility" ) )

    
    # st.plotly_chart(fig, title='Simulated Portfolio Optimization based on Efficient Frontier')
    return [markdown_str, fig]

def run_ef_with_random(stock_data): 

    #inputs for the variables above
    returns = stock_data.pct_change()
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    num_portfolios = 5000
    risk_free_rate = 0.02

    #To display the frontier and data:
    return display_simulated_ef_with_random(stock_data, mean_returns, cov_matrix, num_portfolios, risk_free_rate)
