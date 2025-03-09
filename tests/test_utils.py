import datetime as dt
import json
from unittest import mock

import pandas as pd
import requests

from src.utils import (
    convert_to,
    get_currency_rates,
    get_stock_price,
    get_stocks_prices,
    greeting,
    read_operations_xlsx,
)


def test_morning():
    assert greeting(dt.datetime(2023, 1, 1, 6, 0)) == "Доброе утро"
    assert greeting(dt.datetime(2023, 1, 1, 11, 59)) == "Доброе утро"


def test_day():
    assert greeting(dt.datetime(2023, 1, 1, 12, 0)) == "Добрый день"
    assert greeting(dt.datetime(2023, 1, 1, 16, 59)) == "Добрый день"


def test_evening():
    assert greeting(dt.datetime(2023, 1, 1, 17, 0)) == "Добрый вечер"
    assert greeting(dt.datetime(2023, 1, 1, 21, 59)) == "Добрый вечер"


def test_night():
    assert greeting(dt.datetime(2023, 1, 1, 22, 0)) == "Доброй ночи"
    assert greeting(dt.datetime(2023, 1, 1, 4, 59)) == "Доброй ночи"


def test_read_operations_xlsx(mocker):
    # Тест доступного файла
    mocker.patch("pandas.read_excel", return_value=pd.DataFrame({"A": [1], "B": [2]}))
    result = read_operations_xlsx("dummy_path.xlsx")
    assert result == [{"A": "1", "B": "2"}]

    # Тест на отсутствие файла
    mocker.patch("pandas.read_excel", side_effect=FileNotFoundError)
    result = read_operations_xlsx("dummy_path.xlsx")
    assert result == "file not found"

    # Тест на другую ошибку
    mocker.patch("pandas.read_excel", side_effect=Exception("Some error"))
    result = read_operations_xlsx("dummy_path.xlsx")
    assert result == "error"


def test_convert_to(mocker):
    # Имитация успешного ответа от API
    mock_response = mock.Mock()
    mock_response.json.return_value = {"result": 75.5}
    mocker.patch("requests.get", return_value=mock_response)

    result = convert_to("USD")
    assert result == 75.5

    # Имитация исключения
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException)
    result = convert_to("USD")
    assert result is None


def test_get_currency_rates(mocker):
    # Имитация файла json с валютами
    mock_user_settings = {"user_currencies": ["USD", "EUR"]}
    mocker.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_user_settings)))

    # Имитация вызова convert_to
    mocker.patch("src.utils.convert_to", side_effect=lambda cur: 75.5 if cur == "USD" else 90.0)

    result = get_currency_rates()
    assert result == [{"currency": "USD", "rate": 75.5}, {"currency": "EUR", "rate": 90.0}]

    # Имитация исключения
    mocker.patch("builtins.open", side_effect=Exception("File not found"))
    result = get_currency_rates()
    assert result == []


def test_get_stock_price(mocker):
    # Имитация успешного ответа от API
    mock_response = mock.Mock()
    mock_response.json.return_value = {
        "Time Series (1min)": {
            "2023-01-01 10:00:00": {"1. open": "100.0"},
            "2023-01-01 10:01:00": {"1. open": "101.0"},
        }
    }
    mocker.patch("requests.get", return_value=mock_response)

    result = get_stock_price("AAPL")
    assert result == 100.0

    # Имитация исключения
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException)
    result = get_stock_price("AAPL")
    assert result is None


def test_get_stocks_prices(mocker):
    # Имитация файла json с акциями
    mock_user_settings = {"user_stocks": ["AAPL", "GOOGL"]}
    mocker.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_user_settings)))

    mocker.patch("src.utils.get_stock_price", side_effect=lambda stock: 100.0 if stock == "AAPL" else 1500.0)

    result = get_stocks_prices()
    assert result == [{"stock": "AAPL", "price": 100.0}, {"stock": "GOOGL", "price": 1500.0}]

    # Имитация исключения
    mocker.patch("builtins.open", side_effect=Exception("File not found"))
    result = get_stocks_prices()
    assert result == []


# if __name__ == "__main__":
#     pytest.main()
