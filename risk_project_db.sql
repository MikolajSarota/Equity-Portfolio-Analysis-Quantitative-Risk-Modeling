CREATE TABLE portfolio (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,

    -- Risk measures
    var FLOAT,
    cvar FLOAT,
    mc_var FLOAT,
    mc_cvar FLOAT,

    -- Performance metrics
    alpha FLOAT,
    beta FLOAT,
    annual_return FLOAT,
    annual_volatility FLOAT,
    sharpe FLOAT,
    correlation FLOAT
);

CREATE TABLE asset (
    id SERIAL PRIMARY KEY,
    portfolio_id INT NOT NULL,
    ticker TEXT NOT NULL,
    weight FLOAT NOT NULL,

    CONSTRAINT fk_portfolio
        FOREIGN KEY (portfolio_id)
        REFERENCES portfolio(id)
);
