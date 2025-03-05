import datetime as dt
import json
from datetime import datetime
from json import dumps
from unittest import mock
from unittest.mock import patch

import pytest

from src.views import get_cards_data, get_top_transactions, main


def test_get_cards_data():
    today = datetime.now().strftime("%d.%m.%Y")  # Текущая дата в нужном формате
    test_data = [
        {"Номер карты": "1234567890123456", "Дата платежа": today, "Сумма операции": -500},
        {"Номер карты": "1234567890123457", "Дата платежа": today, "Сумма операции": -300},
        {
            "Номер карты": "1234567890123456",
            "Дата платежа": today,
            "Сумма операции": 100,
        },  # Игнорируем положительные суммы
        {
            "Номер карты": 1234567890123456,
            "Дата платежа": today,
            "Сумма операции": -200,
        },  # Неверный формат номера карты
        {
            "Номер карты": "1234567890123458",
            "Дата платежа": "01.01.2023",
            "Сумма операции": -100,
        },  # Дата не совпадает
        {"Номер карты": "1234567890123459", "Дата платежа": today, "Сумма операции": -400},
    ]

    expected_result = [
        {"last_digits": "3456", "total_spent": "500.00", "cashback": "5.00"},
        {"last_digits": "3457", "total_spent": "300.00", "cashback": "3.00"},
        {"last_digits": "3459", "total_spent": "400.00", "cashback": "4.00"},
    ]

    result = get_cards_data(test_data)

    # Проверяем, что результат соответствует ожиданиям
    assert result == expected_result


def test_get_cards_data_empty():
    # Проверка на пустые данные
    result = get_cards_data([])
    assert result == []


def test_get_cards_data_invalid_date():
    # Проверка на неправильный формат даты
    test_data = [
        {"Номер карты": "1234567890123456", "Дата платежа": "invalid date", "Сумма операции": -500},
    ]

    result = get_cards_data(test_data)
    assert result == []


def test_get_cards_data_short_card_number():
    # Проверка на короткий номер карты
    test_data = [
        {"Номер карты": "123", "Дата платежа": datetime.now().strftime("%d.%m.%Y"), "Сумма операции": -500},
    ]

    result = get_cards_data(test_data)
    assert result == []  # Ожидаем пустой результат, поскольку номер карты некорректен


def test_get_cards_data_invalid_card_number_type():
    # Проверка на неверный тип номера карты
    test_data = [
        {
            "Номер карты": 1234567890123456,
            "Дата платежа": datetime.now().strftime("%d.%m.%Y"),
            "Сумма операции": -500,
        },
    ]

    result = get_cards_data(test_data)
    assert result == []  # Ожидаем пустой результат, поскольку номер карты некорректен


def test_get_top_transactions():
    # Задаем тестовые данные
    test_data = [
        {"Дата платежа": "2023-01-01", "Сумма платежа": 100, "Категория": "Food", "Описание": "Dinner"},
        {"Дата платежа": "2023-01-02", "Сумма платежа": 200, "Категория": "Transport", "Описание": "Taxi"},
        {
            "Дата платежа": "2023-01-03",
            "Сумма платежа": -300,
            "Категория": "Utilities",
            "Описание": "Electricity",
        },
        {"Дата платежа": "2023-01-04", "Сумма платежа": 400, "Категория": "Health", "Описание": "Gym"},
        {"Дата платежа": "2023-01-05", "Сумма платежа": 500, "Категория": "Shopping", "Описание": "Mall"},
        {"Дата платежа": "2023-01-06", "Сумма платежа": 50, "Категория": "Fun", "Описание": "Cinema"},
    ]

    expected_result = [
        {"date": "2023-01-05", "amount": 500, "category": "Shopping", "description": "Mall"},
        {"date": "2023-01-04", "amount": 400, "category": "Health", "description": "Gym"},
        {"date": "2023-01-03", "amount": -300, "category": "Utilities", "description": "Electricity"},
        {"date": "2023-01-02", "amount": 200, "category": "Transport", "description": "Taxi"},
        {"date": "2023-01-01", "amount": 100, "category": "Food", "description": "Dinner"},
    ]

    # Вызов функции
    result = get_top_transactions(test_data)

    # Проверка результата
    assert result == expected_result[:5]


def test_get_top_transactions_empty():
    # Проверка на пустые данные
    result = get_top_transactions([])
    assert result == []


@mock.patch("src.views.read_operations_xlsx")
@mock.patch("src.views.greeting")
@mock.patch("src.views.get_cards_data")
@mock.patch("src.views.get_top_transactions")
@mock.patch("src.views.get_currency_rates")
@mock.patch("src.views.get_stocks_prices")
def test_main(
    mock_get_stocks_prices,
    mock_get_currency_rates,
    mock_get_top_transactions,
    mock_get_cards_data,
    mock_greeting,
    mock_read_operations_xlsx,
):
    # Подготавливаем данные
    mock_read_operations_xlsx.return_value = [{}]  # Как пример, файл операций возвращает пустой словарь
    mock_greeting.return_value = "Доброе утро"
    mock_get_cards_data.return_value = [{"last_digits": "9012", "total_spent": "0.00", "cashback": "0.00"}]
    mock_get_top_transactions.return_value = [
        {"date": "15.01.2023", "amount": "-500", "category": "Еда", "description": "Ужин в ресторане"}
    ]
    mock_get_currency_rates.return_value = []
    mock_get_stocks_prices.return_value = []

    # Вызов функции main
    result_date = dt.datetime.now()
    result = main(result_date)

    # Ожидаемая структура результата
    expected_result = {
        "greeting": "Доброе утро",
        "cards": [{"last_digits": "9012", "total_spent": "0.00", "cashback": "0.00"}],
        "top_transactions": [
            {"date": "15.01.2023", "amount": "-500", "category": "Еда", "description": "Ужин в ресторане"}
        ],
        "currency_rates": [],
        "stock_prices": [],
    }

    # Проверяем, что результат соответствует ожидаемому результату
    assert json.loads(result) == expected_result


# if __name__ == "__main__":
#     pytest.main()
