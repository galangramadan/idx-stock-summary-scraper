from datetime import datetime
import os
import sys
import tempfile
from dotenv import load_dotenv
import pandas as pd
import psycopg
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

    _ = load_dotenv()
    db_uri = os.getenv("DATABASE_URI")

    if db_uri is None or db_uri == "":
        print("Error: DATABASE_URI in .env is not set.")
        sys.exit(1)

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"Temporary directory created at: {temp_dir}")

        file_path = download_excel_file(temp_dir, date)
        df = pd.read_excel(file_path)
        df["Date"] = date
        stock_summary_data = list(zip(df["Kode Saham"], df["Date"], df["Penutupan"], df["Volume"], df["Nilai"], df["Foreign Sell"], df["Foreign Buy"]))
        companies_data = set(zip(df["Kode Saham"], df["Nama Perusahaan"]))

        with psycopg.connect(db_uri) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT ticker, company_name FROM companies"
                )
                current_companies_data = set(cur.fetchall())
                missing_companies_data = companies_data - current_companies_data

                if missing_companies_data:
                    print(f"Adding {missing_companies_data} to dabase.")
                    cur.executemany(
                        "INSERT INTO companies(ticker, company_name) VALUES (%s, %s)",
                        missing_companies_data
                    )

                cur.execute(
                    "SELECT date FROM stock_summary"
                )
                row = cur.fetchone()

                if row is None:
                    print(f"Adding stock summary data for {date} to dabase.")
                    cur.executemany(
                        "INSERT INTO stock_summary(ticker, date, close_price, volume, value, foreign_sell, foreign_buy) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        stock_summary_data
                    )
                else:
                    print(f"Stock summary data for {date} are already saved in database.")

                conn.commit()

    except DataNotFoundError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
