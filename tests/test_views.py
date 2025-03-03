import pytest
import datetime as dt
from unittest import mock
from src.views import get_cards_data, get_top_transactions, main


def test_get_cards_data():
    cards = [
        {
            "Номер карты": "1234 5678 9012 3456",
            "Дата платежа": "15.01.2023",
            "Сумма операции": "-500",
        },
        {
            "Номер карты": "1234 5678 9012 3456",
            "Дата платежа": "05.01.2023",
            "Сумма операции": "-150",
        },
        {
            "Номер карты": "1111 2222 3333 4444",
            "Дата платежа": "15.01.2023",
            "Сумма операции": "100",
        },
        {
            "Номер карты": 1234567890123456,  # Неверный формат
            "Дата платежа": "15.01.2023",
            "Сумма операции": "-200",
        },
    ]

    # Получаем сегодняшнюю дату
    today = dt.date.today()

    # Вызов функции с тестовыми данными
    result = get_cards_data(cards)

    # Проверяем, что возвращаемые данные соответствуют ожиданиям
    expected_result = [
        {
            "last_digits": "9012 3456",
            "total_spent": "0.00",
            "cashback": "0.00",
        },
        {
            "last_digits": "3333 4444",
            "total_spent": "0.00",
            "cashback": "0.00",
        },
    ]

    assert result == expected_result


def test_get_top_transactions():
    # Подготовка тестовых данных
    transactions = [
        {
            "Дата платежа": "15.01.2023",
            "Сумма платежа": "-500",
            "Категория": "Еда",
            "Описание": "Ужин в ресторане",
        },
        {
            "Дата платежа": "15.01.2023",
            "Сумма платежа": "-1500",
            "Категория": "Покупки",
            "Описание": "Покупка одежды",
        },
        {
            "Дата платежа": "15.01.2023",
            "Сумма платежа": "3000",
            "Категория": "Зарплата",
            "Описание": "Заработная плата",
        },
        {
            "Дата платежа": "15.01.2023",
            "Сумма платежа": "-1200",
            "Категория": "Техника",
            "Описание": "Покупка телефона",
        },
    ]

    # Вызов функции
    result = get_top_transactions(transactions)

    # Ожидаемый результат
    expected_result = [
        {
            "date": "15.01.2023",
            "amount": "-1500",
            "category": "Покупки",
            "description": "Покупка одежды",
        },
        {
            "date": "15.01.2023",
            "amount": "-1200",
            "category": "Техника",
            "description": "Покупка телефона",
        },
        {
            "date": "15.01.2023",
            "amount": "-500",
            "category": "Еда",
            "description": "Ужин в ресторане",
        },
        {
            "date": "15.01.2023",
            "amount": "3000",
            "category": "Зарплата",
            "description": "Заработная плата",
        },
    ]

    assert result == expected_result[:5]  # Проверяем только 5 лучших транзакций


@mock.patch('your_module_name.read_operations_xlsx')
@mock.patch('your_module_name.greeting')
@mock.patch('your_module_name.get_cards_data')
@mock.patch('your_module_name.get_top_transactions')
@mock.patch('your_module_name.get_currency_rates')
@mock.patch('your_module_name.get_stocks_prices')
@mock.patch('json.dumps')
def test_main(mock_dumps, mock_get_stocks_prices, mock_get_currency_rates, mock_get_top_transactions,
              mock_get_cards_data, mock_greeting, mock_read_operations_xlsx):
    # Подготавливаем данные
    mock_read_operations_xlsx.return_value = [{}]  # Как пример, файл операций возвращает пустой словарь
    mock_greeting.return_value = "Доброе утро"
    mock_get_cards_data.return_value = [{"last_digits": "9012", "total_spent": "0.00", "cashback": "0.00"}]
    mock_get_top_transactions.return_value = [
        {"date": "15.01.2023", "amount": "-500", "category": "Еда", "description": "Ужин в ресторане"}]
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
            {"date": "15.01.2023", "amount": "-500", "category": "Еда", "description": "Ужин в ресторане"}],
        "currency_rates": [],
        "stock_prices": [],
    }

    mock_dumps.assert_called_once_with(expected_result, ensure_ascii=False, indent=4)

    assert json.loads(result) == expected_result


if __name__ == "__main__":
    pytest.main()