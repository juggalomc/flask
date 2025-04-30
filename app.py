from flask import Flask, render_template, request
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import talib
from sklearn.linear_model import LogisticRegression

app = Flask(__name__)

def analyze_stock(symbol):
    try:
        # Fetch data
        end_date = datetime.today()
        start_date = end_date - timedelta(days=365)
        df = yf.download(symbol, start=start_date, end=end_date)

        if df.empty:
            return None, "No data found."

        # Indicators
        df['SMA'] = talib.SMA(df['Close'], timeperiod=14)
        df['RSI'] = talib.RSI(df['Close'], timeperiod=14)
        macd, macdsignal, _ = talib.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
        df['MACD'] = macd
        df['MACD_Signal'] = macdsignal

        df.dropna(inplace=True)

        # ML features
        df['Return'] = df['Close'].pct_change()
        df['Target'] = df['Return'].shift(-1).apply(lambda x: 1 if x > 0 else 0)
        df.dropna(inplace=True)

        features = df[['SMA', 'RSI', 'MACD', 'MACD_Signal']]
        target = df['Target']

        model = LogisticRegression()
        model.fit(features, target)

        latest_data = df.iloc[-1][['SMA', 'RSI', 'MACD', 'MACD_Signal']]
        prediction = model.predict([latest_data])[0]

        return "BUY" if prediction == 1 else "SELL", None

    except Exception as e:
        return None, str(e)

@app.route('/', methods=['GET', 'POST'])
def index():
    signal = None
    error = None

    if request.method == 'POST':
        symbol = request.form['symbol']
        signal, error = analyze_stock(symbol)

    return render_template('index.html', signal=signal, error=error)

if __name__ == '__main__':
    app.run(debug=True)
