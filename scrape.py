from playwright.sync_api import Browser, Page, Playwright, sync_playwright

def launch_browser() -> tuple[Playwright, Browser, Page]:
    """Launches a Playwright instance, browser, and opens the website page.    

    Returns:
        A tuple containing the Playwright instance, the Browser instance, and the Page object representing the opened webpage.
    """

    playwright_instance = sync_playwright().start()
    browser = playwright_instance.chromium.launch(headless=False) # Set headless=False to avoid bot detection.
    url = "https://www.idx.co.id/id/data-pasar/ringkasan-perdagangan/ringkasan-saham/"
    page = browser.new_page()
    _ = page.goto(url)

    return playwright_instance, browser, page

def download_excel_file(dir_path: str, date: str, page: Page) -> str | None:
    """Downloads an Excel file containing stock summary data from IDX website based on the given date.

    Args:
        dir_path: The directory to save the downloaded file.
        date: The date for which to download the stock summary data (YYYY-MM-DD format).
        page: Page object respresenting the opened webpage.

    Returns:
        The full path to the downloaded file.
    """

    date_input = page.locator("[name='date']")
    date_input.fill(date)
    date_input.press("Enter")

    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(500)

    download_button = page.locator(".btn-download")
    if download_button.get_attribute("disabled") == "disabled":
        print(f"Skip: Stock summary for {date} is not found.")
        return
    with page.expect_download() as download_info:
        _ = download_button.click()
    download = download_info.value

    file_path = dir_path + "/" + download.suggested_filename
    download.save_as(file_path)
    print(f"Stock summary file for {date} is saved to: {file_path}")
    return file_path
