import logging
import requests
from common.logging.error.error import Error
from playwright.sync_api import sync_playwright
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR


class RedfinClient:
    def __init__(self, base_url: str, user_agent: str):
        """
        Client for interacting with Redfin's autocomplete location API.
        """
        self.base_url = base_url
        self.user_agent = user_agent
        self.headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.redfin.com/",
            "Connection": "keep-alive",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1"
        }

    def fetch_location_suggestions(self, postal_code: str) -> tuple:
        """
        Calls Redfin's location autocomplete API with a ZIP code.
        :param postal_code: ZIP code string to search locations for.
        :return: JSON response containing location suggestions.
        """
        logging.info(START_OF_METHOD)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, devtools=True)
            page = browser.new_page()

            # Navigate to Redfin home
            page.goto("https://www.redfin.com/zipcode/60452", wait_until="load")

            # Type ZIP code into search box and submit
            page.wait_for_selector('#search-box-input', timeout=10000)
            page.click('#search-box-input')  # focus input
            page.type('#search-box-input', postal_code, delay=100)
            page.press('#search-box-input', 'Enter')

            # Wait for navigation and grab results
            page.wait_for_selector(".HomeCardContainer", timeout=10000)
            html = page.content()

            browser.close()
            return html, 200
