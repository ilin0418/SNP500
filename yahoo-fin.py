import yfinance as yf
import pandas as pd
import csv

def get_entire_stock_snp500():
    # Open the CSV file
    with open('SNP_500_Tickers.csv', mode='r') as f:
        reader = csv.DictReader(f)  # Use DictReader to handle headers
        # Extract the 'Symbol' column from each row
        tickers = [row['Symbol'] for row in reader]
    return tickers

def get_stock_info(stock):
    stock = yf.Ticker(stock)
    return stock.info

def main():
    get = get_stock_info("AAPL")
    print   (get)

if __name__ == '__main__':
    main()