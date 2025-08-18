from datetime import datetime
import os
import sys
import tempfile
from dotenv import load_dotenv
import pandas as pd
from database_operations import upsert_data_to_database
from scrape import download_excel_file, launch_browser
from utils import date_range

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: uv run main.py <YYYY-MM-DD> <YYYY-MM-DD>\nSecond argument is optional.")
        sys.exit(1)

    for i in range(1, len(sys.argv)):
        try:
            _ = datetime.strptime(sys.argv[i], '%Y-%m-%d')
        except ValueError:
            print("Date is not valid, use <YYYY-MM-DD> format.")
            sys.exit(1)

    dates = [sys.argv[1]]

    if len(sys.argv) == 3:
        start_date = sys.argv[1]
        end_date = sys.argv[2]
        dates = date_range(start_date, end_date)

    _ = load_dotenv()
    db_uri = os.getenv("DATABASE_URI")

    if db_uri is None or db_uri == "":
        print("Error: DATABASE_URI in .env is not set.")
        sys.exit(1)

    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Temporary directory created at: {temp_dir}")
        
        playwright_instance = None
        browser = None

        try:
            playwright_instance, browser, page = launch_browser()

            for date in dates:
                file_path = download_excel_file(temp_dir, date, page)
                if file_path:
                    df = pd.read_excel(file_path)
                    df["Date"] = date
                    stock_summary_data = list(zip(df["Kode Saham"], df["Date"], df["Penutupan"], df["Volume"], df["Nilai"], df["Foreign Sell"], df["Foreign Buy"]))
                    companies_data = set(zip(df["Kode Saham"], df["Nama Perusahaan"]))
                    _ = upsert_data_to_database(db_uri, date, companies_data, stock_summary_data)

        finally:
            if browser:
                browser.close()
            if playwright_instance:
                playwright_instance.stop()

if __name__ == "__main__":
    main()
