# S&P 500 Tools

This project provides tools for analyzing S&P 500 stocks, including a web interface for searching stock information and viewing stock price charts.

## Features

- Search for S&P 500 stocks by ticker symbol.
- View detailed stock information, including market cap, revenue, net income, and more.
- Display stock price charts with interactive range selectors.

## Prerequisites

- Node.js
- Python 3.x
- Redis

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/snp500-tools.git
   cd snp500-tools
   ```

2. Install frontend dependencies:

   ```bash
   cd stock-terminal
   npm install
   ```

3. Install backend dependencies:

   ```bash
   cd ../
   pip install -r requirements.txt
   ```

4. Create a `redis_account.json` file in the root directory with your Redis connection details:

   ```json
   {
     "host": "your_redis_host",
     "port": your_redis_port,
     "password": "your_redis_password"
   }
   ```

## Usage

1. Start the backend server:

   ```bash
   python pythonAPI.py
   ```

2. Start the frontend development server:

   ```bash
   cd stock-terminal
   npm run dev
   ```

3. Open your browser and navigate to `http://localhost:3000`.

## API Endpoints

### `/api/processTicker`

- **Method:** POST
- **Description:** Processes the ticker symbol and returns stock information.
- **Request Body:**
  ```json
  {
    "ticker": "AAPL"
  }
  ```
- **Response:**
  ```json
  {
    "message": "Ticker received",
    "ticker": "AAPL",
    "stock_info": {
      "name": "Apple Inc.",
      "ticker": "AAPL",
      // ...other stock information...
    }
  }
  ```

### `/api/stockGraph`

- **Method:** POST
- **Description:** Returns stock price chart data for the given ticker symbol.
- **Request Body:**
  ```json
  {
    "ticker": "AAPL"
  }
  ```
- **Response:**
  ```json
  {
    "graph": {
      "labels": ["2023-01-01", "2023-01-02", ...],
      "datasets": [
        {
          "label": "Close Price",
          "data": [150.0, 152.0, ...],
          "borderColor": "rgba(75, 192, 192, 1)",
          "backgroundColor": "rgba(75, 192, 192, 0.2)",
          "fill": false
        }
      ]
    }
  }
  ```

## License

This project is licensed under the MIT License.
