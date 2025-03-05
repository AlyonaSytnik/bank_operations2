import datetime as dt
import json
import logging
from functools import wraps

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def report(default_filename: str = "report.json"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            filename = kwargs.get("filename", default_filename)
            try:
                if isinstance(result, pd.DataFrame):
                    result.to_json(filename, orient="records", force_ascii=False)
                else:
                    with open(filename, "w") as f:
                        json.dump(result, f, ensure_ascii=False, indent=4)
                logger.info(f"Отчет сохранен в файл: {filename}")
            except Exception as e:
                logger.error(f"Ошибка при записи отчета в файл: {e}")

            return result

        return wrapper

    return decorator


@report(default_filename="spend_report.json")
def spent(
    transactions: pd.DataFrame,
    category: str,
    date=dt.datetime.now().strftime("%d.%m.%Y"),
) -> pd.DataFrame:
    try:
        current_date = dt.datetime.strptime(date, "%d.%m.%Y")
        start_date = current_date - dt.timedelta(days=90)
        data = transactions[
            (transactions["Категория"] == category)
            & (pd.to_datetime(transactions["Дата платежа"], format="%d.%m.%Y") >= start_date)
            & (pd.to_datetime(transactions["Дата платежа"], format="%d.%m.%Y") <= current_date)
        ]

        return data
    except Exception as e:
        logger.error(f"Ошибка при формировании отчета: {e}")
        return pd.DataFrame()
