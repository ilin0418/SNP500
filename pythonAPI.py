from flask import Flask, request, jsonify
from flask_cors import CORS
import redis
import json
import yfinance as yf

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow all origins for API endpoints

# Initialize Redis client with your Redis database connection details
REDIS_HOST = 'redis-13709.c329.us-east4-1.gce.redns.redis-cloud.com'  # Hostname or IP address
REDIS_PORT = 13709  # Port number
REDIS_PASSWORD = '4XiiB1a58OjM9Vb9TzAMTjuah3cLN3Ru'  # Password

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
except redis.ConnectionError:
    redis_client = None
    print("Could not connect to Redis")

@app.route('/api/processTicker', methods=['POST'])
def handle_ticker():
    data = request.get_json()
    ticker = data.get('ticker')
    
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

    if ('Close', ticker) not in df.columns:
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
    
    print("Graph data prepared:", graph_data)
    return jsonify({"graph": graph_data})

def generateStockInfo(ticker):
    stock = yf.Ticker(ticker)
    return {
        "name": stock.info.get("shortName", "Unknown"),
        "ticker": ticker,
        "info": stock.info
    }

if __name__ == '__main__':
    app.run(debug=True)
