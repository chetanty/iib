from flask import Flask, jsonify
from forecast import fetch_data, analyze_data

app = Flask(__name__)
api_key = 'OFFVBKZJ8RFRP8YF'  # Replace with your actual API key
@app.route('/')
def index():
    return "Welcome to the AAPL Forecast App!"
@app.route('/forecast')
def forecast():
    df = fetch_data(api_key)
    forecast_data = analyze_data(df)
    return jsonify(forecast_data)

if __name__ == '__main__':
    app.run(debug=True)
