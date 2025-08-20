from datetime import date, datetime, timedelta
import os
import sys
import tempfile
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import psycopg
from scrape import (
    download_excel_file,
    save_stock_summary_data,
    transform_data,
    update_companies_data,
)


def get_list_dates() -> list[str]:
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print(
            "Usage: uv run main.py <YYYY-MM-DD> <YYYY-MM-DD>\nSecond argument is optional."
        )
        sys.exit(1)

    for i in range(1, len(sys.argv)):
        try:
            _ = datetime.strptime(sys.argv[i], "%Y-%m-%d")
        except ValueError:
            print("Date is not valid, use <YYYY-MM-DD> format.")
            sys.exit(1)

    dates = [sys.argv[1]]
    if len(sys.argv) == 3:
        start_date = date.fromisoformat(sys.argv[1])
        end_date = date.fromisoformat(sys.argv[2])
        if start_date <= end_date:
            current_date = start_date + timedelta(days=1)
            while current_date <= end_date:
                dates.append(current_date.strftime("%Y-%m-%d"))
                current_date += timedelta(days=1)
        else:
            current_date = start_date - timedelta(days=1)
            while current_date >= end_date:
                dates.append(current_date.strftime("%Y-%m-%d"))
                current_date -= timedelta(days=1)

    return dates


def main():
    dates = get_list_dates()
    _ = load_dotenv()
    db_uri = os.getenv("DATABASE_URI")
    if db_uri is None or db_uri == "":
        print("Error: DATABASE_URI in .env is not set.")
        sys.exit(1)

    conn = psycopg.connect(db_uri)
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"Temporary directory created at: {temp_dir}")
            with sync_playwright() as p:
                url = "https://www.idx.co.id/id/data-pasar/ringkasan-perdagangan/ringkasan-saham/"
                browser = p.chromium.launch(
                    headless=False
                )  # Set headless=False to avoid Cloudflare detection.
                page = browser.new_page()
                _ = page.goto(url)
                for date in dates:
                    file_path = download_excel_file(temp_dir, page, date)
                    if file_path:
                        companies_data, stock_summary_data = transform_data(
                            file_path, date
                        )
                        _ = update_companies_data(conn, companies_data)
                        _ = save_stock_summary_data(conn, stock_summary_data, date)

    except Exception as e:
        print(f"Unexpected error: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
