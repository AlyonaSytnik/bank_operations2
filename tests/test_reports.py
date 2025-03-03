import datetime as dt
import unittest
from unittest.mock import patch

import pandas as pd
from src.reports import spent


class TestSpentFunction(unittest.TestCase):

    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('pandas.DataFrame.to_json')
    @patch('src.reports.logger')
    def test_spent_function_writes_to_file(self, mock_logger, mock_to_json, mock_open):
        # Подготовка данных для теста
        transactions = pd.DataFrame({
            "Категория": ["A", "B", "A"],
            "Дата платежа": ["01.01.2025", "01.02.2025", "01.03.2025"],
            "Сумма": [100, 200, 150]
        })

        # Установка даты для теста
        category = "A"
        date = "01.03.2025"

        # Вызов функции
        result = spent(transactions, category, date=date)

        # Проверка, что результат является DataFrame
        self.assertIsInstance(result, pd.DataFrame)

        # Проверка, что метод to_json был вызван
        mock_to_json.assert_called_once_with("spend_report.json", orient="records", force_ascii=False)

        # Проверяем, что корректные данные были получены
        expected_data = transactions[transactions["Категория"] == category]
        expected_data = expected_data[
            (pd.to_datetime(expected_data["Дата платежа"], format="%d.%m.%Y") <= dt.datetime.strptime(date, "%d.%m.%Y"))
        ]
        pd.testing.assert_frame_equal(result, expected_data)

        # Проверка логирования
        mock_logger.info.assert_called_once_with("Отчет сохранен в файл: spend_report.json")

    @patch('src.reports.logger')
    def test_spent_function_handling_errors(self, mock_logger):
        with patch('builtins.open', side_effect=IOError("Unable to write file.")):
            transactions = pd.DataFrame()
            result = spent(transactions, "A")

            # Проверка, что вернулся пустой DataFrame
            self.assertTrue(result.empty)

            # Проверка логирования об ошибке
            #mock_logger.error.any_call("Ошибка при записи отчета в файл: Unable to write file.")


if __name__ == "__main__":
    unittest.main()
