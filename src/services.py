import datetime as dt
import json
import logging
from pathlib import Path

from src.utils import read_operations_xlsx


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_cashback_category(data, year, month):
    try:
        transactions = []

        for item in data:
            # Убедимся, что "Дата платежа" - строка
            if isinstance(item["Дата платежа"], str):
                try:
                    # Пробуем разобрать дату
                    transaction_date = dt.datetime.strptime(item["Дата платежа"], "%d.%m.%Y")

                    # Проверяем год и месяц
                    if transaction_date.year == year and transaction_date.month == month:
                        transactions.append(item)
                except ValueError:
                    # Логируем предупреждение о некорректной дате
                    logger.warning(f"Неверный формат даты: {item['Дата платежа']}, транзакция пропущена.")

        categories = {}
        for transaction in transactions:
            category = transaction.get("Категория")
            cashback = transaction.get("Кэшбэк")
            if category and cashback:
                categories[category] = categories.get(category, 0) + cashback

        # Сортируем категории по кэшбэку
        sorted_categories = dict(
            sorted(categories.items(), key=lambda item: item[1], reverse=True)
        )
        return json.dumps(sorted_categories, ensure_ascii=False, indent=4)

    except Exception as e:
        logger.error(f"Ошибка при анализе данных: {e}")
        return json.dumps({}, ensure_ascii=False)


if __name__ == "__main__":
    BASE_DIR = Path(__file__).parent
    print(
        analyze_cashback_category(
            read_operations_xlsx(BASE_DIR.parent / "data" / "operations.xlsx"),
            2021,
            3,
        )
    )
