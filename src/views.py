import datetime as dt
from json import dumps
from pathlib import Path

from utils import (
    greeting,
    read_operations_xlsx,
    get_currency_rates,
    get_stocks_prices,
)


BASE_DIR = Path(__file__).parent
OPERATIONS_PATH = BASE_DIR.parent / "data" / "operations.xlsx"


def get_cards_data(cards):
    result = []
    insert_cards = {}
    now = dt.date.today()
    for card in cards:
        if type(card_number := card["Номер карты"]) != str:
            continue
        card_date = dt.datetime.strptime(card["Дата платежа"], "%d.%m.%Y").strftime("%Y-%m-%d")
        card_date = dt.datetime.strptime(card_date, "%Y-%m-%d")

        if card_date.month == now.month and 1 <= card_date.day <= now.day and card_date.year == now.year:
            card_number = card_number[1:]
            insert_cards[card_number] = insert_cards.get(card_number, 0) + (
                card_spent * (-1)
                if (card_spent := int(card["Сумма операции"])) < 0
                else 0
            )
    for card_number, spent in insert_cards.items():
        result.append({
            "last_digits": card_number,
            "total_spent": f"{spent:.2f}",
            "cashback": f"{(spent / 100):.2f}",
        })
    return result


def get_top_transactions(data):
    result = []
    data = {abs(obj["Сумма платежа"]): obj for obj in data}.values()
    top_transactions = sorted(data, key=lambda x: abs(x["Сумма платежа"]), reverse=True)[:5]
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


def main(date: dt.datetime):
    operations_file = read_operations_xlsx(OPERATIONS_PATH)
    greet = greeting(date)
    cards = get_cards_data(operations_file)
    top_transactions = get_top_transactions(operations_file)
    currency_rates = get_currency_rates()
    stock_prices = get_stocks_prices()

    result = {
        "greeting": greet,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
    return dumps(result, ensure_ascii=False, indent=4)