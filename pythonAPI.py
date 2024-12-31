from flask import Flask, request, jsonify
from flask_cors import CORS
import redis
import json
import yfinance as yf

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow all origins for API endpoints

# Load Redis connection details from JSON file
with open('redis_account.json', 'r') as f:
    redis_config = json.load(f)

REDIS_HOST = redis_config['host']
REDIS_PORT = redis_config['port']
REDIS_PASSWORD = redis_config['password']

try:
    redis_client = redis.StrictRedis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        db=0,
        decode_responses=True
    )
    redis_client.ping()
    print("Connected to Redis")
    # Clear the Redis cache on boot
except redis.ConnectionError:
    redis_client = None
    print("Could not connect to Redis")

def clear_cache():
    if redis_client:
        redis_client.flushdb()
        print("Redis cache cleared")

@app.route('/api/processTicker', methods=['POST'])
def handle_ticker():
    data = request.get_json()
    ticker = data.get('ticker')

    if not ticker:
        return jsonify({"error": "No ticker provided"}), 400
    
    if redis_client:
        # Check if the ticker is in the cache
        stock_info = redis_client.get(ticker)
        if stock_info:
            stock_info = json.loads(stock_info)
            print(f"Cache hit for ticker: {ticker}")
        else:
            # Fetch stock info and store it in the cache
            stock_info = generateStockInfo(ticker)
            redis_client.set(ticker, json.dumps(stock_info))
            print(f"Cache miss for ticker: {ticker}")
    else:
        # Fetch stock info without caching
        stock_info = generateStockInfo(ticker)
        print(f"Fetched stock info for ticker: {ticker}")

    return jsonify({"message": "Ticker received", "ticker": ticker, "stock_info": stock_info})

@app.route('/api/stockGraph', methods=['POST'])
def stock_graph():
    data = request.get_json()
    ticker = data.get('ticker')
    df = yf.download(tickers=ticker, period='5y', interval='1d')

    if 'Close' not in df.columns:
        return jsonify({"error": "Data not available"}), 500
    
    graph_data = {
        "labels": df.index.strftime('%Y-%m-%d').tolist(),
        "datasets": [{
            "label": "Close Price",
            "data": df[('Close', ticker)].tolist(),
            "borderColor": "rgba(75, 192, 192, 1)",
            "backgroundColor": "rgba(75, 192, 192, 0.2)",
            "fill": False
        }]
    }
    
    # print("Graph data prepared:", graph_data)
    return jsonify({"graph": graph_data})

def abbreviate_number(num):
    try:
        num = float(num)
    except (ValueError, TypeError):
        return "N/A"
    
    if num >= 1_000_000_000_000:
        return f"{num / 1_000_000_000_000:.2f}T"
    elif num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.2f}K"
    else:
        return str(num)

def generateStockInfo(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "name": info.get("shortName", "Unknown"),
        "ticker": ticker,
        "marketCap": abbreviate_number(info.get("marketCap", "N/A")),
        "totalRevenue": abbreviate_number(info.get("totalRevenue", "N/A")),
        "netIncomeToCommon": abbreviate_number(info.get("netIncomeToCommon", "N/A")),
        "dividendYield": info.get("dividendYield", "N/A"),
        "sharesOutstanding": f"{info.get('sharesOutstanding', 'N/A') / 1e9:.2f}B",
        "trailingPE": info.get("trailingPE", "N/A"),
        "trailingEps": info.get("trailingEps", "N/A"),
        "forwardPE": info.get("forwardPE", "N/A"),
        "dividendRate": f"${info.get('dividendRate', 'N/A')} ({info.get('dividendYield', 'N/A') * 100:.2f}%)",
        "exDividendDate": info.get("exDividendDate", "N/A"),

        "volume": abbreviate_number(info.get('volume', 'N/A')),
        "open": info.get("open", "N/A"),
        "previousClose": info.get("previousClose", "N/A"),
        "dayLow": info.get("dayLow", "N/A"),
        "dayHigh": info.get("dayHigh", "N/A"),
        "fiftyTwoWeekRange": f"{info.get('fiftyTwoWeekLow', 'N/A')} - {info.get('fiftyTwoWeekHigh', 'N/A')}",
        "beta": info.get("beta", "N/A"),
        "recommendation": info.get("recommendationKey", "N/A").capitalize(),
        "targetMeanPrice": info.get("targetMeanPrice", "N/A"),
        "earningsDate": info.get("earningsDate", "N/A")
    }

if __name__ == '__main__':    app.run(debug=True)
