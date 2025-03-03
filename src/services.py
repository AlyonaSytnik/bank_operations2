import datetime as dt
import json
import logging
from pathlib import Path

from utils import read_operations_xlsx


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_cashback_category(data, year, month):
    try:
        transactions = list(
            filter(
                lambda x: dt.datetime.strptime(
                    x["Дата платежа"], "%d.%m.%Y"
                ).year
                == year
                and dt.datetime.strptime(x["Дата платежа"], "%d.%m.%Y").month
                == month,
                filter(lambda x: type(x["Дата платежа"]) == str, data),
            )
        )

        categories = {}
        for transaction in transactions:
            category = transaction.get("Категория")
            cashback = transaction.get("Кэшбэк")
            if category and cashback:
                categories[category] = categories.get(category, 0) + cashback

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
