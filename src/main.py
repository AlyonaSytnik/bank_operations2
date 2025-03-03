from pathlib import Path
import pandas as pd
import datetime as dt

from utils import read_operations_xlsx
from views import main
from services import analyze_cashback_category
from reports import spent


BASE_DIR = Path(__file__).parent
OPERATIONS_PATH = BASE_DIR.parent / "data" / "operations.xlsx"


if __name__ == "__main__":
    transactions = list(
        filter(
            lambda x: type(x["Дата платежа"]) == str,
            read_operations_xlsx(BASE_DIR.parent / "data" / "operations.xlsx"),
        )
    )
    # main = main(dt.datetime.now())
    services = analyze_cashback_category(
        transactions,
        2021,
        9,
    )
    reports = spent(pd.DataFrame(transactions), "Супермаркеты")
