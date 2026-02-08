import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

from risk import TRADING_DAYS, portfolio_summary, VAR, CVAR
from monte_carlo import monte_carlo

from db import insert_portfolio


portfolio_tickers = [
 "TSLA", "NVDA", "AMD", "COIN", "META"
]
benchmark = "^GSPC"
start_date = "2018-01-01"
end_date = "2025-01-01"

prices = yf.download(
    tickers=portfolio_tickers + [benchmark],
    start=start_date,
    end=end_date,
    auto_adjust=True,
    progress=True
)["Close"].dropna() 

weights = {ticker: 1 / len(portfolio_tickers) for ticker in portfolio_tickers}

portfolio = portfolio_summary(prices, weights, benchmark)
portfolio_returns = portfolio["portfolio_returns"]
benchmark_returns = portfolio["benchmark_returns"]
summary = portfolio["summary"]

hist_var_95 = VAR(portfolio_returns, alfa=0.95)
hist_cvar_95 = CVAR(portfolio_returns, alfa=0.95)

simulated_daily_returns, price_paths = monte_carlo(portfolio_returns)

simulated_simple_returns = np.exp(simulated_daily_returns) - 1
mc_var_95 = VAR(simulated_simple_returns.flatten(), alfa=0.95)
mc_cvar_95 = CVAR(simulated_simple_returns.flatten(), alfa=0.95)

beta = summary["beta"]
annual_portfolio_return = summary["annual_return"]
annual_market_return = benchmark_returns.mean() * TRADING_DAYS
rf = 0.04
alpha = annual_portfolio_return - (rf + beta * (annual_market_return - rf))

benchmark_log_returns = np.log(prices[benchmark] / prices[benchmark].shift(1)).dropna()
benchmark_path = np.exp(benchmark_log_returns.cumsum())
benchmark_path = benchmark_path.iloc[-TRADING_DAYS:]
benchmark_path = benchmark_path / benchmark_path.iloc[0]

sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 6))

for i in range(50):
    plt.plot(price_paths[i], alpha=0.3)

plt.plot(
    benchmark_path.values,
    color="black",
    linewidth=2,
    label="S&P 500 (historical)"
)

plt.title("Monte Carlo Portfolio Paths vs S&P 500")
plt.xlabel("Days")
plt.ylabel("Portfolio Value")
plt.legend()
plt.show()

sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 6))
sns.histplot(
    simulated_daily_returns.flatten(),
    bins=100,
    stat="density",
    alpha=0.3
)
plt.axvline(mc_var_95, color="red", linestyle="--", linewidth=2, label="VaR 95%")
plt.axvline(mc_cvar_95, color="darkred", linestyle="--", linewidth=2, label="CVaR 95%")
plt.title("Distribution of Simulated Daily Portfolio Losses")
plt.legend()
plt.show()

print("\nPORTFOLIO RISK SUMMARY\n")
print(f"Annual Return: {summary['annual_return']:.2%}")
print(f"Annual Volatility: {summary['annual_volatility']:.2%}")
print(f"Sharpe Ratio: {summary['sharpe']:.2f}")
print(f"Beta vs Benchmark: {beta:.2f}")
print(f"CAPM Alpha: {alpha:.2%}")
print(f"Correlation with Benchmark: {summary['correlation_with_benchmark']:.2f}")
print(f"Historical VaR (95%, 1-day): {hist_var_95:.2%}")
print(f"Historical CVaR (95%, 1-day): {hist_cvar_95:.2%}")
print(f"Monte Carlo VaR (95%, 1-day): {mc_var_95:.2%}")
print(f"Monte Carlo CVaR (95%, 1-day): {mc_cvar_95:.2%}")

insert_portfolio(
    name="MyPortfolio",
    hist_var=hist_var_95,
    hist_cvar=hist_cvar_95,
    mc_var=mc_var_95,
    mc_cvar=mc_cvar_95,
    alpha=alpha,
    beta=beta,
    annual_return=summary["annual_return"],
    annual_volatility=summary["annual_volatility"],
    sharpe=summary["sharpe"],
    correlation=summary["correlation_with_benchmark"],
    weights=weights
)
