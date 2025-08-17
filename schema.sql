CREATE DATABASE idx_scraper;

\c idx_scraper

CREATE TABLE companies (
	ticker VARCHAR(10) NOT NULL,
	company_name VARCHAR(255) NOT NULL,
	PRIMARY KEY (ticker)
);

CREATE TABLE stock_summary (
	ticker VARCHAR(10) NOT NULL, 
	close_price INTEGER NOT NULL,
	volume BIGINT NOT NULL,
	value BIGINT NOT NULL,
	foreign_buy BIGINT NOT NULL,
	foreign_sell BIGINT NOT NULL,
	date DATE NOT NULL,
	PRIMARY KEY (ticker, date),
	CONSTRAINT fk_companies FOREIGN KEY(ticker) REFERENCES companies(ticker) ON DELETE CASCADE;
);

\dt
