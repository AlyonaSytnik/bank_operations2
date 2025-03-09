import datetime as dt
import json
from pathlib import Path
from typing import Any

from src.utils import (
    get_currency_rates,
    get_stocks_prices,
    greeting,
    read_operations_xlsx,
)

BASE_DIR: Path = Path(__file__).parent
OPERATIONS_PATH: Path = BASE_DIR.parent / "data" / "operations.xlsx"


def get_cards_data(cards: list[dict[str, str]]) -> list[dict[str, str]]:
    """
    Извлекает данные о картах и суммах операций за текущий день.

    Args:
        cards (list[dict[str, str]]): Список словарей с данными о картах.

    Returns:
        list[dict[str, str]]: Список словарей с последними четырьмя цифрами номера карты, общей потраченной суммой
        и кэшбэком.
    """
    result: list[dict[str, str]] = []
    insert_cards: dict[str, float] = {}
    now: dt.date = dt.date.today()

    for card in cards:
        if not isinstance(card.get("Номер карты"), str) or len(card["Номер карты"]) < 4:
            continue

        try:
            card_date: dt.date = dt.datetime.strptime(card["Дата платежа"], "%d.%m.%Y %H:%M:%S").date()
        except ValueError:
            continue  # Если есть проблемы с форматом даты, пропускаем запись

        if card_date.month == now.month and 1 <= card_date.day <= now.day and card_date.year == now.year:
            card_number: str = card["Номер карты"][-4:]  # Берем последние 4 символа
            card_spent: int = int(card["Сумма операции"])
            if card_spent < 0:  # Учитываем только отрицательные суммы
                insert_cards[card_number] = insert_cards.get(card_number, 0) + abs(card_spent)

    for card_number, spent in insert_cards.items():
        result.append(
            {
                "last_digits": card_number,
                "total_spent": f"{spent:.2f}",
                "cashback": f"{(spent / 100):.2f}",
            }
        )
    return result


def get_top_transactions(data: list[dict[str, str]]) -> list[dict[str, str]]:
    """
    Получает топ-5 транзакций по сумме платежа.

    Args:
        data (list[dict[str, str]]): Список транзакций.

    Returns:
        list[dict[str, str]]: Список словарей с данными о топ-5 транзакциях.
    """
    result: list[dict[str, str]] = []
    if not data:
        return result  # Возвращаем пустой список, если данных нет

    top_transactions: list[dict[str, str]] = sorted(
        data, key=lambda x: abs(float(x["Сумма платежа"])), reverse=True
    )[:5]
    for transaction in top_transactions:
        result.append(
            {
                "date": transaction["Дата платежа"],
                "amount": transaction["Сумма платежа"],
                "category": transaction["Категория"],
                "description": transaction["Описание"],
            }
        )
    return result


def main(date: dt.datetime) -> str:
    """
    Объединяет выполнение нескольких функций и возвращает результаты в виде JSON-строки.

    Args:
        date (dt.datetime): Дата и время для приветствия и анализа данных.

    Returns:
        str: JSON-строка с приветствием, данными о картах, топ-транзакциями, курсами валют и ценами акций.
    """
    operations_file: list[dict[str, str]] = read_operations_xlsx(OPERATIONS_PATH)
    greet: str = greeting(date)
    cards: list[dict[str, str]] = get_cards_data(operations_file)
    top_transactions: list[dict[str, str]] = get_top_transactions(operations_file)
    currency_rates: list[dict[str, str | float]] = get_currency_rates()
    stock_prices: list[dict[str, str | float]] = get_stocks_prices()

    result: dict[str, Any] = {
        "greeting": greet,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
    return json.dumps(result, ensure_ascii=False, indent=4)
