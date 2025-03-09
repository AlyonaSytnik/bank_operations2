import json
import unittest

from src.services import analyze_cashback_category


class TestAnalyzeCashbackCategory(unittest.TestCase):

    def setUp(self):
        self.data = [
            {"Дата платежа": "15.01.2023", "Категория": "Еда", "Кэшбэк": 100},
            {"Дата платежа": "20.01.2023", "Категория": "Техника", "Кэшбэк": 150},
            {"Дата платежа": "15.02.2023", "Категория": "Еда", "Кэшбэк": 200},
            {"Дата платежа": "10.01.2023", "Категория": "Техника", "Кэшбэк": 50},
            {"Дата платежа": "05.01.2023", "Категория": "Одежда", "Кэшбэк": 70},
            {"Дата платежа": "01.01.2023", "Категория": "Еда", "Кэшбэк": 200},
            {
                "Дата платежа": "28.02.2023",
                "Категория": "Еда",
                "Кэшбэк": 300,
            },  # Эта дата не будет учитывать Январь
        ]

    def test_analyze_cashback_category_january(self):
        expected_result = {
            "Еда": 300,
            "Техника": 200,
            "Одежда": 70,
        }
        result = json.loads(analyze_cashback_category(self.data, 2023, 1))
        self.assertEqual(result, expected_result)

    def test_analyze_cashback_category_february(self):
        expected_result = {
            "Еда": 500,
        }
        result = json.loads(analyze_cashback_category(self.data, 2023, 2))
        self.assertEqual(result, expected_result)

    def test_analyze_cashback_category_no_transactions(self):
        expected_result = {}
        result = json.loads(analyze_cashback_category(self.data, 2023, 3))
        self.assertEqual(result, expected_result)

    def test_analyze_cashback_category_invalid_date(self):
        expected_result = {
            "Еда": 300,
            "Техника": 200,
            "Одежда": 70,
        }
        result = json.loads(analyze_cashback_category(self.data, 2023, 1))
        self.assertEqual(result, expected_result)


# if __name__ == '__main__':
#     unittest.main()
