import datetime as dt
import json
import logging
import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


load_dotenv()


BASE_DIR = Path(__file__).parent
USER_SETTINGS_PATH = BASE_DIR.parent / "user_settings.json"
OPERATIONS_XLSX_PATH = BASE_DIR.parent / "data" / "operations.xlsx"


CURRENCY_API_URL = "https://api.apilayer.com/currency_data/convert"
STOCK_API_URL = "https://www.alphavantage.co/query"
CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY")
STOCK_API_KEY = os.getenv("STOCK_API_KEY")


def greeting(date: dt.datetime):
    hours = date.hour
    if 5 <= hours <= 11:
        return "Доброе утро"
    elif 12 <= hours <= 16:
        return "Добрый день"
    elif 17 <= hours <= 21:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def read_operations_xlsx(path):
    try:
        df = pd.read_excel(path, na_filter=True)
        df.fillna(value=0, inplace=True)
        return df.to_dict("records")
    except FileNotFoundError:
        return "file not found"
    except Exception as e:
        logger.error(f"Ошибка при чтении файла: {e}")
        return "error"


def convert_to(from_cur: str, to_cur: str = "RUB", amount: float = 1):
    try:
        response = requests.get(
            CURRENCY_API_URL,
            params={"to": to_cur, "from": from_cur, "amount": amount},
            headers={"apikey": CURRENCY_API_KEY},
        )
        return round(response.json()["result"], 2)
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при конвертации валюты: {e}")
        return None


def get_currency_rates():
    result = []
    try:
        with open(USER_SETTINGS_PATH) as f:
            data = json.load(f)
            for currency in data["user_currencies"]:
                rate = convert_to(currency)
                if rate is not None:
                    result.append({"currency": currency, "rate": rate})
    except Exception as e:
        logger.error(f"Ошибка при получении курсов валют: {e}")
    return result


def get_stock_price(symbol: str):
    try:
        response = requests.get(
            STOCK_API_URL,
            params={
                "function": "TIME_SERIES_INTRADAY",
                "symbol": symbol,
                "interval": "1min",
                "apikey": STOCK_API_KEY,
            },
        )
        data = response.json()
        time_series = data.get("Time Series (1min)")
        if time_series:
            latest_time = next(iter(time_series))
            latest_price = time_series[latest_time]["1. open"]
            return float(latest_price)
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при получении цены акции {symbol}: {e}")
    return None


def get_stocks_prices():
    result = []
    try:
        with open(USER_SETTINGS_PATH) as f:
            data = json.load(f)
            for stock in data["user_stocks"]:
                price = get_stock_price(stock)
                if price is not None:
                    result.append({"stock": stock, "price": price})
    except Exception as e:
        logger.error(f"Ошибка при получении цен акций: {e}")
    return result
