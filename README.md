# Stock_Portfolio
Stock Portfolio management program made using python &amp; sql

Create a database called stock_portfolio in mysql:

CREATE DATABASE stock_portfolio;
USE stock_portfolio;


Now create 3 tables in SQL:

CREATE TABLE Portfolio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_symbol VARCHAR(20),
    quantity INT,
    purchase_price DECIMAL(10, 2),
    current_price DECIMAL(10, 2) DEFAULT 0,
    profit_loss DECIMAL(10, 2) DEFAULT 0,
    total_invested DECIMAL(10, 2) DEFAULT 0,
    total_current_value DECIMAL(10, 2) DEFAULT 0
);

CREATE TABLE SoldStocks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_symbol VARCHAR(20),
    purchase_price DECIMAL(10, 2),
    sell_price DECIMAL(10, 2),
    quantity INT,
    profit_loss DECIMAL(10, 2),
    sell_date DATE
);

CREATE TABLE PortfolioSummary (
    id INT AUTO_INCREMENT PRIMARY KEY,
    total_invested DECIMAL(10, 2),
    total_current_value DECIMAL(10, 2),
    total_profit_loss DECIMAL(10, 2)
);


Run the Python program to enter the data in the table.


To view the details, run the following command in mysql:
SELECT * FROM Portfolio;
SELECT * FROM SoldStocks;
SELECT * FROM PortfolioSummary;
