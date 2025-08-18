import psycopg
from exceptions import DataExistsError

def upsert_data_to_database(db_uri: str, date: str, companies_data: set[tuple[(str, str)]], stock_summary_data: list[tuple[(str, str, int, int, int, int, int )]]):
    with psycopg.connect(db_uri) as conn:
        with conn.cursor() as cur:
            _ = cur.execute(
                "SELECT ticker, company_name FROM companies"
            )
            current_companies_data = set(cur.fetchall())
            missing_companies_data = companies_data - current_companies_data

            if missing_companies_data:
                print("Found missing companies.")
                for company_data in missing_companies_data:
                    ticker = company_data[0]
                    company_name = company_data[1]
                    _ = cur.execute(
                        "SELECT ticker FROM companies WHERE ticker = %s",
                        (ticker,)
                    )
                    row = cur.fetchone()
                    if row is None:
                        print(f"Adding {company_data} to dabase.")
                        _ = cur.execute(
                            "INSERT INTO companies(ticker, company_name) VALUES (%s, %s)",
                            company_data
                        )
                    else:
                        print(f"Updating {ticker} data.")
                        _ = cur.execute(
                            "UPDATE companies SET company_name = %s WHERE ticker = %s",
                            (company_name, ticker)
                        )

            _ = cur.execute(
                "SELECT date FROM stock_summary WHERE date = %s",
                (date,)
            )
            row = cur.fetchone()

            if row is None:
                print(f"Adding stock summary data for {date} to dabase.")
                cur.executemany(
                    "INSERT INTO stock_summary(ticker, date, close_price, volume, value, foreign_sell, foreign_buy) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    stock_summary_data
                )
            else:
                raise DataExistsError(f"Stock summary data for {date} are already saved in the database!")

            conn.commit()
            print(f"Stock summary data for {date} has been saved successfully.")
