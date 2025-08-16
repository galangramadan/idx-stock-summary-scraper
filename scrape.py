from playwright.sync_api import sync_playwright
from exceptions import DataNotFoundError

def download_excel_file(dir_path: str, date: str) -> str :
    """Downloads an Excel file containing stock summary data from IDX website based on the given date.

    Args:
        dir_path: The directory to save the downloaded file.
        date: The date for which to download the stock summary data (YYYY-MM-DD format).

    Returns:
        The full path to the downloaded file.

    Raises:
        DataNotFoundError: If the stock summary data for the specified date is not found.
    """
    with sync_playwright() as p:
        url = "https://www.idx.co.id/id/data-pasar/ringkasan-perdagangan/ringkasan-saham/"
        browser = p.chromium.launch(headless=False) # Set headless=False to avoid Cloudflare detection.
        page = browser.new_page()
        _ = page.goto(url)

        date_input = page.locator("[name='date']")
        date_input.fill(date)
        date_input.press("Enter")

        page.wait_for_load_state("networkidle")

        download_button = page.locator(".btn-download")
        if download_button.get_attribute("disabled") == "disabled":
            raise DataNotFoundError(f"Stock summary for {date} is not found.")
        with page.expect_download() as download_info:
            _ = download_button.click()
        download = download_info.value

        file_path = dir_path + "/" + download.suggested_filename
        download.save_as(file_path)
        print(f"Stock summary file for {date} is saved to: {file_path}")
        browser.close()
        return file_path
