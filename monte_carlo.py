import numpy as np


def monte_carlo(portfolio_returns, n_simulations=10_000, TRADING_DAYS=252):
    mu = portfolio_returns.mean()
    sigma = portfolio_returns.std()

    simulated_daily_returns = np.random.normal(
        loc=mu,
        scale=sigma,
        size=(n_simulations, TRADING_DAYS)
    )

    cumulative_log_returns = simulated_daily_returns.cumsum(axis=1)
    price_paths = np.exp(cumulative_log_returns)

    return simulated_daily_returns, price_paths
