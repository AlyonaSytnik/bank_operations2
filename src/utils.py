import datetime as dt
import json
import logging
import os
from pathlib import Path
from typing import Optional, Union

import pandas as pd
import requests
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger: logging.Logger = logging.getLogger(__name__)

load_dotenv()

BASE_DIR: Path = Path(__file__).parent
USER_SETTINGS_PATH: Path = BASE_DIR.parent / "user_settings.json"
OPERATIONS_XLSX_PATH: Path = BASE_DIR.parent / "data" / "operations.xlsx"

CURRENCY_API_URL: str = "https://api.apilayer.com/currency_data/convert"
STOCK_API_URL: str = "https://www.alphavantage.co/query"
CURRENCY_API_KEY: Optional[str] = os.getenv("CURRENCY_API_KEY")
STOCK_API_KEY: Optional[str] = os.getenv("STOCK_API_KEY")


def greeting(date: dt.datetime) -> str:
    """
    Возвращает приветствие в зависимости от времени суток.

    Args:
        date (dt.datetime): Дата и время для определения приветствия.

    Returns:
        str: Приветствие ("Доброе утро", "Добрый день", "Добрый вечер" или "Доброй ночи").
    """
    hours: int = date.hour
    if 5 <= hours <= 11:
        return "Доброе утро"
    elif 12 <= hours <= 16:
        return "Добрый день"
    elif 17 <= hours <= 21:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def read_operations_xlsx(path: Path) -> Union[str, list[dict[str, str]]]:
    """
    Читает операции из файла Excel и возвращает их в виде списка словарей.

    Args:
        path (Path): Путь к файлу Excel.

    Returns:
        Union[str, list[dict[str, str]]]: Список операций в виде словарей или сообщение об ошибке.
    """
    try:
        df: pd.DataFrame = pd.read_excel(path, na_filter=True)
        df.fillna(value=0, inplace=True)
        # Приводим данные к нужному типу
        records: list[dict[str, str]] = [
            {str(k): str(v) for k, v in record.items()} for record in df.to_dict("records")
        ]
        return records
    except FileNotFoundError:
        return "file not found"
    except Exception as e:
        logger.error(f"Ошибка при чтении файла: {e}")
        return "error"


def convert_to(from_cur: str, to_cur: str = "RUB", amount: float = 1) -> Optional[float]:
    """
    Конвертирует указанную сумму из одной валюты в другую.

    Args:
        from_cur (str): Код валюты, из которой нужно конвертировать.
        to_cur (str): Код валюты, в которую нужно конвертировать. По умолчанию "RUB".
        amount (float): Сумма для конвертации. По умолчанию 1.

    Returns:
        Optional[float]: Конвертированная сумма или None в случае ошибки.
    """
    try:
        response: requests.Response = requests.get(
            CURRENCY_API_URL,
            params={"to": to_cur, "from": from_cur, "amount": amount},
            headers={"apikey": CURRENCY_API_KEY},
        )
        result: float = float(response.json()["result"])
        return round(result, 2)
    except (requests.exceptions.RequestException, ValueError, KeyError) as e:
        logger.error(f"Ошибка при конвертации валюты: {e}")
        return None


def get_currency_rates() -> list[dict[str, Union[str, float]]]:
    """
    Получает курсы валют для пользовательских валют.

    Returns:
        list[dict[str, Union[str, float]]]: Список словарей с кодами валют и их курсами.
    """
    result: list[dict[str, Union[str, float]]] = []
    try:
        with open(USER_SETTINGS_PATH) as f:
            data: dict[str, str] = json.load(f)
            for currency in data["user_currencies"]:
                rate: Optional[float] = convert_to(currency)
                if rate is not None:
                    result.append({"currency": currency, "rate": rate})
    except Exception as e:
        logger.error(f"Ошибка при получении курсов валют: {e}")
    return result


def get_stock_price(symbol: str) -> Optional[float]:
    """
    Получает текущую цену акции по ее символу.

    Args:
        symbol (str): Символ акции.

    Returns:
        Optional[float]: Текущая цена акции или None в случае ошибки.
    """
    try:
        response: requests.Response = requests.get(
            STOCK_API_URL,
            params={
                "function": "TIME_SERIES_INTRADAY",
                "symbol": symbol,
                "interval": "1min",
                "apikey": STOCK_API_KEY,
            },
        )
        data: Union[dict[str, str], str] = response.json()
        if isinstance(data, dict):
            time_series: dict[str, str] = data.get("Time Series (1min)", {})
            if time_series:
                latest_time: str = next(iter(time_series))
                latest_price: str = time_series[latest_time]["1. open"]
                return float(latest_price)
    except (requests.exceptions.RequestException, ValueError, KeyError) as e:
        logger.error(f"Ошибка при получении цены акции {symbol}: {e}")
    return None


def get_stocks_prices() -> list[dict[str, Union[str, float]]]:
    """
    Получает текущие цены акций для пользовательских акций.

    Returns:
        list[dict[str, Union[str, float]]]: Список словарей с символами акций и их ценами.
    """
    result: list[dict[str, Union[str, float]]] = []
    try:
        with open(USER_SETTINGS_PATH) as f:
            data: dict[str, str] = json.load(f)
            for stock in data["user_stocks"]:
                price: Optional[float] = get_stock_price(stock)
                if price is not None:
                    result.append({"stock": stock, "price": price})
    except Exception as e:
        logger.error(f"Ошибка при получении цен акций: {e}")
    return result
