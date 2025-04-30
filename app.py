from flask import Flask, render_template, request
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from sklearn.linear_model import LogisticRegression
from bot import StockAnalysisBot  # Assuming your class is in bot.py
import os

app = Flask(__name__)

bot = StockAnalysisBot()

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    if request.method == "POST":
        symbol = request.form.get("symbol", "").upper().strip()
        if not symbol:
            error = "Please enter a stock symbol."
        else:
            df = bot.get_data(symbol, days=bot.HISTORICAL_DAYS)
            if df is None or df.empty:
                error = f"No data found for symbol: {symbol}"
            else:
                try:
                    df = bot.calculate_technical_indicators(df)
                    fib = bot.calculate_fibonacci_levels(df)
                    momentum = bot.calculate_momentum(df)
                    trend = bot.predict_trend(df)
                    entry_exit = bot.calculate_entry_exit(df, fib, df['close'].iloc[-1], df['close'].pct_change().std())
                    targets = {'bullish': fib, 'bearish': fib}  # Placeholder for now, could expand
                    pattern = bot.generate_trade_pattern(df, targets, momentum, trend, entry_exit)

                    result = {
                        'symbol': symbol,
                        'momentum': momentum,
                        'trend': trend,
                        'entry_exit': entry_exit,
                        'pattern': pattern
                    }
                except Exception as e:
                    error = f"Error processing data: {e}"
    return render_template("index.html", result=result, error=error)

if __name__ == "__main__":
    app.run(debug=True)
