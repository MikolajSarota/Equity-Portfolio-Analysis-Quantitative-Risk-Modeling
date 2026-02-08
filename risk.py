import numpy as np
import pandas as pd

TRADING_DAYS = 252


def log_returns(prices):
    returns = np.log(prices / prices.shift(1))
    return returns.dropna()


def annual_return(returns):
    return returns.mean() * TRADING_DAYS


def annual_volatility(returns):
    return returns.std() * np.sqrt(TRADING_DAYS)


def corr(returns):
    return returns.corr()


def betas(returns, tickers, benchmark_ticker):
    benchmark_returns = returns[benchmark_ticker]
    benchmark_variance = benchmark_returns.var()

    betas_dict = {}
    for ticker in tickers:
        covariance = returns[ticker].cov(benchmark_returns)
        betas_dict[ticker] = covariance / benchmark_variance

    return pd.Series(betas_dict, name="Beta")


def sharpe(returns, rf=0.04):
    excess_return = annual_return(returns) - rf
    return excess_return / annual_volatility(returns)


def alpha(returns, tickers, benchmark_ticker, rf=0.04):
    annual_returns = returns.mean() * TRADING_DAYS
    market_return = annual_returns[benchmark_ticker]
    beta_series = betas(returns, tickers, benchmark_ticker)

    alpha_dict = {}
    for ticker in tickers:
        actual_return = annual_returns[ticker]
        expected_return = rf + beta_series[ticker] * (market_return - rf)
        alpha_dict[ticker] = actual_return - expected_return

    return pd.Series(alpha_dict, name="CAPM Alpha")


def VAR(returns, alfa=0.95):
    losses = -returns
    return np.quantile(losses, alfa)


def CVAR(returns, alfa=0.95):
    losses = -returns
    var_level = np.quantile(losses, alfa)
    return losses[losses >= var_level].mean()


def portfolio_summary(prices, weights, benchmark, alfa=0.95):
    returns = log_returns(prices)
    weights = pd.Series(weights).reindex(returns.columns.drop(benchmark))

    if not np.isclose(weights.sum(), 1):
        raise ValueError("Weights must sum to 1")

    portfolio_returns = (returns[weights.index] * weights).sum(axis=1)
    benchmark_returns = returns[benchmark]

    summary = {
        "annual_return": annual_return(portfolio_returns),
        "annual_volatility": annual_volatility(portfolio_returns),
        "sharpe": sharpe(portfolio_returns),
        "beta": portfolio_returns.cov(benchmark_returns) / benchmark_returns.var(),
        "correlation_with_benchmark": portfolio_returns.corr(benchmark_returns),
        "var": VAR(portfolio_returns, alfa),
        "cvar": CVAR(portfolio_returns, alfa)
    }

    return {
        "portfolio_returns": portfolio_returns,
        "benchmark_returns": benchmark_returns,
        "summary": summary,
        "weights": weights
    }
