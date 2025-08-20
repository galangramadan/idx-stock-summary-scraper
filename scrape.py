import pandas as pd
from playwright.sync_api import Page
from psycopg.connection import Connection


def update_companies_data(
    conn: Connection, companies_data: set[tuple[(str, str)]]
) -> None:
    with conn.cursor() as cur:
        _ = cur.execute("SELECT ticker, company_name FROM companies")
        current_companies_data = set(cur.fetchall())
        missing_companies_data = companies_data - current_companies_data

        if missing_companies_data:
            print("Found missing company data.")
            for company_data in missing_companies_data:
                ticker = company_data[0]
                company_name = company_data[1]
                _ = cur.execute(
                    "SELECT ticker FROM companies WHERE ticker = %s", (ticker,)
                )
                row = cur.fetchone()
                if row is None:
                    print(f"Adding {company_data} to dabase.")
                    _ = cur.execute(
                        "INSERT INTO companies(ticker, company_name) VALUES (%s, %s)",
                        company_data,
                    )
                else:
                    print(f"Updating {ticker} data.")
                    _ = cur.execute(
                        "UPDATE companies SET company_name = %s WHERE ticker = %s",
                        (company_name, ticker),
                    )

            conn.commit()


def save_stock_summary_data(
    conn: Connection,
    stock_summary_data: list[tuple[(str, str, int, int, int, int, int)]],
    date: str,
):
    with conn.cursor() as cur:
        _ = cur.execute("SELECT date FROM stock_summary WHERE date = %s", (date,))
        row = cur.fetchone()

        if row is None:
            print(f"Adding stock summary data for {date} to dabase.")
            cur.executemany(
                "INSERT INTO stock_summary(ticker, date, close_price, volume, value, foreign_sell, foreign_buy) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                stock_summary_data,
            )
        else:
            print(
                f"Skip: Stock summary data for {date} already exists in the database!"
            )
            return

        conn.commit()
        print(f"Stock summary data for {date} has been saved successfully.")


def download_excel_file(temp_dir: str, page: Page, date: str) -> str | None:
    page.wait_for_load_state("networkidle")  # Wait for initial load.
    page.wait_for_timeout(500)
    date_input = page.locator("[name='date']")
    date_input.fill(date)
    date_input.press("Enter")
    page.wait_for_load_state("networkidle")  # Wait after selecting date.
    page.wait_for_timeout(500)
    download_button = page.locator(".btn-download")
    if download_button.get_attribute("disabled") == "disabled":
        print(f"Skip: Stock summary for {date} is not found.")
        return

    with page.expect_download() as download_info:
        _ = download_button.click()

    download = download_info.value
    file_path = temp_dir + "/" + download.suggested_filename
    download.save_as(file_path)
    print(f"Stock summary file for {date} is saved to: {file_path}")
    return file_path


def transform_data(
    file_path: str, date: str
) -> tuple[set[tuple[(str, str)]], list[tuple[(str, str, int, int, int, int, int)]]]:
    df = pd.read_excel(file_path)
    df["Date"] = date
    stock_summary_data = list(
        zip(
            df["Kode Saham"],
            df["Date"],
            df["Penutupan"],
            df["Volume"],
            df["Nilai"],
            df["Foreign Sell"],
            df["Foreign Buy"],
        )
    )
    companies_data = set(zip(df["Kode Saham"], df["Nama Perusahaan"]))
    return companies_data, stock_summary_data
