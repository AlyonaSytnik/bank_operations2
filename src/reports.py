import datetime as dt
import json
import logging
from functools import wraps
from typing import Any, Callable, Union

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger: logging.Logger = logging.getLogger(__name__)


def report(default_filename: str = "report.json") -> Callable:
    """
    Декоратор для сохранения результата выполнения функции в файл в формате JSON.

    Args:
        default_filename (str): Имя файла по умолчанию для сохранения отчета. По умолчанию 'report.json'.

    Returns:
        Callable: Декоратор, который оборачивает заданную функцию.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Union[pd.DataFrame, dict]:
            result: Union[pd.DataFrame, dict] = func(*args, **kwargs)
            filename: str = kwargs.get("filename", default_filename)
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
    date: str = dt.datetime.now().strftime("%d.%m.%Y"),
) -> pd.DataFrame:
    """
    Формирует отчет о расходах по заданной категории за последние 90 дней.

    Args:
        transactions (pd.DataFrame): Датафрейм с данными о транзакциях.
        category (str): Категория расходов для фильтрации.
        date (str): Дата в формате "дд.мм.гггг" для анализа. По умолчанию установлена текущая дата.

    Returns:
        pd.DataFrame: Датафрейм с отфильтрованными транзакциями.
    """
    try:
        current_date: dt.datetime = dt.datetime.strptime(date, "%d.%m.%Y")
        start_date: dt.datetime = current_date - dt.timedelta(days=90)
        data: pd.DataFrame = transactions[
            (transactions["Категория"] == category)
            & (pd.to_datetime(transactions["Дата платежа"], format="%d.%m.%Y") >= start_date)
            & (pd.to_datetime(transactions["Дата платежа"], format="%d.%m.%Y") <= current_date)
        ]
        return data
    except Exception as e:
        logger.error(f"Ошибка при формировании отчета: {e}")
        return pd.DataFrame()
