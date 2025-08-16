from datetime import datetime
import sys
import tempfile
import pandas as pd
from exceptions import DataNotFoundError
from scrape import download_excel_file

def main():
    if len(sys.argv) != 2:
        print("Usage: uv run main.py <YYYY-MM-DD>")
        sys.exit(1)

    date = sys.argv[1]

    try:
        _ = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        print("Date is not valid, use <YYYY-MM-DD> format.")
        sys.exit(1)

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"Temporary directory created at: {temp_dir}")

        file_path = download_excel_file(temp_dir, date)
        raw_data = pd.read_excel(file_path)
        print(raw_data.head())

        # TODO: Process the data.

        # TODO: Database integration.
    except DataNotFoundError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
