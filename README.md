# Bank operations

## Installation

1. Clone the repository:
```
git clone https://github.com/AlyonaSytnik/bank_operations2.git
```
2. Navigate to the project directory:
```
cd Proj1
```
3. Install the required dependencies:
```
pip install -r requirements.txt
```

## Usage

1. Run the main script:
```
python main.py
```

## API

The project provides the following API endpoints:

1. `analyze_cashback_category(data, year, month)`: Analyzes the cashback categories for the given year and month.
2. `spent(transactions, category, date)`: Generates a report of the spending in the specified category within the last 90 days.

## Contributing

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature`.
3. Make your changes and commit them: `git commit -am 'Add some feature'`.
4. Push to the branch: `git push origin feature/your-feature`.
5. Submit a pull request.

## Testing

To run the tests, execute the following command:

```
python -m unittest discover -s tests -p "test_*.py"
```

Alternatively, you can use a testing framework like `pytest`:

```
pytest tests/
```

The project includes the following test files:

- `test_reports.py`
- `test_services.py`
- `test_utils.py`
- `test_views.py`