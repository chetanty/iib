import numpy as np
import pandas as pd
import requests
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import warnings

def fetch_data(api_key, symbol='AAPL', interval='5min'):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    
    key = f'Time Series ({interval})'
    if key not in data:
        raise ValueError(f"Error: '{key}' not found in the response.")
    
    df = pd.DataFrame(data[key]).T
    df = df.astype(float)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    print("Initial data:\n", df.head())
    return df

def analyze_data(df):
    # Ensure proper datetime index and frequency
    df.index = pd.to_datetime(df.index)
    df = df.asfreq('5min', fill_value=np.nan)
    
    # Handle missing values
    df['4. close'] = df['4. close'].ffill()
    
    # Apply transformations
    df['4. close'] = np.log(df['4. close'])
    df['4. close_diff'] = df['4. close'].diff().dropna()
    
    print("Transformed data:\n", df.head())
    
    # Check stationarity
    result = adfuller(df['4. close_diff'].dropna())
    print("ADF Statistic:", result[0])
    print("p-value:", result[1])
    if result[1] > 0.05:
        raise ValueError("Data is not stationary even after differencing.")
    
    # Fit ARIMA model
    try:
        model = ARIMA(df['4. close_diff'].dropna(), order=(1,1,1))  # Simpler model
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model_fit = model.fit()
        
        print(model_fit.summary())
    except Exception as e:
        print(f"Model fitting error: {e}")
        return {"error": str(e)}
    
    # Forecast the next 30 intervals (adjust as needed)
    try:
        forecast_steps = 30
        forecast_results = model_fit.get_forecast(steps=forecast_steps)
        
        forecast_mean = forecast_results.predicted_mean
        forecast_conf_int = forecast_results.conf_int()
        
        if forecast_mean.empty:
            raise ValueError("Forecast mean is empty.")
        
        forecast_index = pd.date_range(start=df.index[-1] + pd.Timedelta(minutes=5), periods=forecast_steps, freq='5min')
        forecast_df = pd.DataFrame(forecast_mean, index=forecast_index, columns=['Forecast'])
        
        forecast_df.index = forecast_df.index.strftime('%Y-%m-%d %H:%M:%S')
        
        print("Forecast:\n", forecast_df.head())
        return forecast_df.to_dict(orient='index')
    except Exception as e:
        print(f"Forecasting error: {e}")
        return {"error": str(e)}
    
# Example usage:
# api_key = 'your_alpha_vantage_api_key'
# df = fetch_data(api_key)
# forecast = analyze_data(df)
