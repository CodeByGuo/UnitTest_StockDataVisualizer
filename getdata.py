import requests
import json
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from datetime import datetime
import re

# Input validation functions
def validate_symbol(symbol):
    return bool(re.match(r'^[A-Z]{1,7}$', symbol))

def validate_chart_type(chart_type):
    return chart_type in ('1', '2')

def validate_time_series(time_series):
    return time_series in ('1', '2', '3', '4')

def validate_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def get_stock_data(symbol, time_series, start_date, end_date, api_key):
    base_url = "https://www.alphavantage.co/query"
    payload = {
        "function": time_series,
        "symbol": symbol,
        "outputsize": "full",
        "apikey": api_key
    }
    if time_series == 'TIME_SERIES_INTRADAY':
        payload['interval'] = '5min'

    response = requests.get(base_url, params=payload)
    response.raise_for_status()

    data = json.loads(response.text)

    if time_series == 'TIME_SERIES_INTRADAY':
        time_series = 'Time Series (5min)'
    elif time_series == 'TIME_SERIES_DAILY_ADJUSTED':
        time_series = 'Time Series (Daily)'
    elif time_series == 'TIME_SERIES_WEEKLY':
        time_series = 'Weekly Time Series'
    elif time_series == 'TIME_SERIES_MONTHLY':
        time_series = 'Monthly Time Series'
    else:
        raise ValueError("Invalid time series")

    open_key = '1. open'
    high_key = '2. high'
    low_key = '3. low'
    close_key = '4. close'

    dates = []
    open_prices = []
    high_prices = []
    low_prices = []
    close_prices = []

    for date_str in data[time_series]:
        if time_series == 'Time Series (5min)':
            date_format = '%Y-%m-%d %H:%M:%S'
        else:
            date_format = '%Y-%m-%d'

        date = datetime.strptime(date_str, date_format)
        if date >= start_date and date <= end_date:
            dates.append(date)
            open_str = data[time_series][date_str][open_key]
            high_str = data[time_series][date_str][high_key]
            low_str = data[time_series][date_str][low_key]
            close_str = data[time_series][date_str][close_key]
            open_prices.append(float(open_str))
            high_prices.append(float(high_str))
            low_prices.append(float(low_str))
            close_prices.append(float(close_str))

    return dates, open_prices, high_prices, low_prices, close_prices

while True:
    try:
        symbol = input("Enter stock symbol: ")
        if not validate_symbol(symbol):
            print("Invalid symbol. Symbol must be 1-7 capitalized alpha characters.")
            continue

        time_series_input = input("Enter time series (1: Intraday, 2: Daily Adjusted, 3: Weekly, 4: Monthly): ")
        if not validate_time_series(time_series_input):
            print("Invalid time series. Please enter 1, 2, 3, or 4.")
            continue

        start_date_str = input("Enter start date (YYYY-MM-DD): ")
        if not validate_date(start_date_str):
            print("Invalid start date. Please enter a valid date in the format YYYY-MM-DD.")
            continue

        end_date_str = input("Enter end date (YYYY-MM-DD): ")
        if not validate_date(end_date_str):
            print("Invalid end date. Please enter a valid date in the format YYYY-MM-DD.")
            continue

        time_series_dict = {
            "1": "TIME_SERIES_INTRADAY",
            "2": "TIME_SERIES_DAILY_ADJUSTED",
            "3": "TIME_SERIES_WEEKLY",
            "4": "TIME_SERIES_MONTHLY",
        }

        time_series = time_series_dict.get(time_series_input)
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        api_key = '9UL3ZIO409JYQX26'
        dates, open_prices, high_prices, low_prices, close_prices = get_stock_data(symbol, time_series, start_date, end_date, api_key)

        chart_type_input = input("Choose a graph type (1: Line, 2: Bar): ")
        if not validate_chart_type(chart_type_input):
            print("Invalid chart type. Please choose 1 for Line or 2 for Bar.")
            continue

        fig, ax = plt.subplots(figsize=(10, 5))

        if chart_type_input == "1":
            ax.plot(dates, close_prices, label="Close")
            ax.plot(dates, open_prices, label="Open")
            ax.plot(dates, low_prices, label="Low")
            ax.plot(dates, high_prices, label="High")
        elif chart_type_input == "2":
            ax.bar(dates, close_prices, label="Close", alpha=0.3)
            ax.bar(dates, open_prices, label="Open", alpha=0.3)
            ax.bar(dates, low_prices, label="Low", alpha=0.3)
            ax.bar(dates, high_prices, label="High", alpha=0.3)

        if time_series == 'TIME_SERIES_INTRADAY':
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
            plt.xticks(rotation=45)
        else:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.xticks(rotation=45)

        ax.set_xlabel('Date')
        ax.set_ylabel('Price ($)')
        ax.set_title(f'{symbol} Stock Prices')
        ax.legend()
        plt.tight_layout()
        plt.show()

        choice = input("Do you want to search for another stock price? (y/n) ")
        if choice.lower() != 'y':
            break

    except (requests.exceptions.HTTPError, ValueError, KeyError, json.JSONDecodeError, KeyboardInterrupt) as e:
        print(f"Error: {e}")
        print("Please try again\n")
