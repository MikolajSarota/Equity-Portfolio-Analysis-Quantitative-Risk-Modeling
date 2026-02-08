from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DB_NAME"
)


def insert_portfolio(
    name,
    hist_var,
    hist_cvar,
    mc_var,
    mc_cvar,
    alpha,
    beta,
    annual_return,
    annual_volatility,
    sharpe,
    correlation,
    weights
):
    with engine.begin() as conn:
        result = conn.execute(
            text("""
            INSERT INTO portfolio (
                name,
                var,
                cvar,
                mc_var,
                mc_cvar,
                alpha,
                beta,
                annual_return,
                annual_volatility,
                sharpe,
                correlation
            )
            VALUES (
                :name,
                :var,
                :cvar,
                :mc_var,
                :mc_cvar,
                :alpha,
                :beta,
                :annual_return,
                :annual_volatility,
                :sharpe,
                :correlation
            )
            RETURNING id
            """),
            {
                "name": name,
                "var": float(hist_var),
                "cvar": float(hist_cvar),
                "mc_var": float(mc_var),
                "mc_cvar": float(mc_cvar),
                "alpha": float(alpha),
                "beta": float(beta),
                "annual_return": float(annual_return),
                "annual_volatility": float(annual_volatility),
                "sharpe": float(sharpe),
                "correlation": float(correlation),
            }
        )

        portfolio_id = result.scalar()

        for ticker, weight in weights.items():
            conn.execute(
                text("""
                INSERT INTO asset (portfolio_id, ticker, weight)
                VALUES (:pid, :ticker, :weight)
                """),
                {
                    "pid": portfolio_id,
                    "ticker": ticker,
                    "weight": float(weight)
                }
            )

        return portfolio_id
