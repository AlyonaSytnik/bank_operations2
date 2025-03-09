from pathlib import Path

import pandas as pd

from src.reports import spent
from src.services import analyze_cashback_category
from src.utils import read_operations_xlsx

BASE_DIR: Path = Path(__file__).parent
OPERATIONS_PATH: Path = BASE_DIR.parent / "data" / "operations.xlsx"


if __name__ == "__main__":
    transactions: list[dict[str, str]] = list(
        filter(
            lambda x: isinstance(x["Дата платежа"], str),
            read_operations_xlsx(BASE_DIR.parent / "data" / "operations.xlsx"),
        )
    )
    # main = main(dt.datetime.now())
    services: str = analyze_cashback_category(transactions, 2021, 9)
    reports: pd.DataFrame = spent(pd.DataFrame(transactions), "Супермаркеты")
