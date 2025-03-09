import datetime as dt
import json
import logging
from pathlib import Path
from typing import Optional

from src.utils import read_operations_xlsx

logging.basicConfig(level=logging.INFO)
logger: logging.Logger = logging.getLogger(__name__)


def analyze_cashback_category(data: list[dict[str, str]], year: int, month: int) -> str:
    """
    Анализирует кэшбэк по категориям для заданного года и месяца.

    Args:
        data (list[dict[str, str]]): Список транзакций, каждая из которых представлена словарем.
        year (int): Год для анализа.
        month (int): Месяц для анализа.

    Returns:
        str: JSON-строка с суммами кэшбэка по категориям или пустая JSON-строка в случае ошибки.
    """
    try:
        transactions: list[dict[str, str]] = []

        for item in data:
            # Убедимся, что "Дата платежа" - строка
            if isinstance(item["Дата платежа"], str):
                try:
                    # Пробуем разобрать дату
                    transaction_date: dt.datetime = dt.datetime.strptime(item["Дата платежа"], "%d.%m.%Y")

                    # Проверяем год и месяц
                    if transaction_date.year == year and transaction_date.month == month:
                        transactions.append(item)
                except ValueError:
                    # Логируем предупреждение о некорректной дате
                    logger.warning(f"Неверный формат даты: {item['Дата платежа']}, транзакция пропущена.")

        categories: dict[str, float] = {}
        for transaction in transactions:
            category: Optional[str] = transaction.get("Категория")
            cashback_str: Optional[str] = transaction.get("Кэшбэк")

            if category and cashback_str:
                try:
                    cashback: float = float(cashback_str)  # Преобразуем строку в float
                    categories[category] = categories.get(category, 0) + cashback
                except ValueError:
                    logger.warning(f"Некорректное значение кэшбэка: {cashback_str}, транзакция пропущена.")

        # Сортируем категории по кэшбэку
        sorted_categories: dict[str, float] = dict(
            sorted(categories.items(), key=lambda item: item[1], reverse=True)
        )
        return json.dumps(sorted_categories, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Ошибка при анализе данных: {e}")
        return json.dumps({}, ensure_ascii=False)


if __name__ == "__main__":
    BASE_DIR: Path = Path(__file__).parent
    print(
        analyze_cashback_category(
            read_operations_xlsx(BASE_DIR.parent / "data" / "operations.xlsx"),
            2021,
            3,
        )
    )
