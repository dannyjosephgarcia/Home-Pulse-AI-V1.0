import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional
import logging
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import WEBSCRAPING_ISSUE
from common.decorators.disabled import disabled

import asyncio
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
import logging
import random
import json


class LowesClient:
    def __init__(self, delay, user_agent, base_url, headless=True, delay_range=(2, 4)):
        self.delay = delay
        self.user_agent = user_agent
        self.base_url = base_url
        self.session = requests.Session()
        self.headless = headless
        self.delay_range = delay_range
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def _initialize_browser(self):
        """Initialize Playwright browser with enhanced stealth settings."""
        self.playwright = await async_playwright().start()

        # Enhanced Chrome arguments for better stealth
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-dev-shm-usage',
                '--disable-extensions',
                '--disable-gpu',
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-field-trial-config',
                '--disable-ipc-flooding-protection',
                '--enable-features=NetworkService,NetworkServiceInProcess',
                '--force-color-profile=srgb',
                '--metrics-recording-only',
                '--use-mock-keychain',
                '--disable-component-extensions-with-background-pages'
            ]
        )

        # More realistic browser context
        self.context = await self.browser.new_context(
            viewport={'width': 1366, 'height': 768},  # Common laptop resolution
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/Chicago',
            permissions=['geolocation'],
            color_scheme='light',
            reduced_motion='no-preference',
            forced_colors='none',
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'max-age=0',
                'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
            }
        )

        # Enhanced stealth scripts
        await self.context.add_init_script("""
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });

            // Mock plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {0: {type: "application/x-google-chrome-pf", suffixes: "pf", description: "Portable Document Format", enabledPlugin: Plugin}},
                    {1: {type: "application/pf", suffixes: "pf", description: "Portable Document Format", enabledPlugin: Plugin}}
                ],
            });

            // Mock languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });

            // Mock permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
            );

            // Mock webGL
            const getParameter = WebGLRenderingContext.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel(R) Iris(R) Plus Graphics 640';
                }
                return getParameter(parameter);
            };

            // Mock chrome object
            Object.defineProperty(window, 'chrome', {
                writable: true,
                enumerable: true,
                configurable: false,
                value: {
                    runtime: {}
                }
            });
        """)

        self.page = await self.context.new_page()

        # Handle potential pop-ups and overlays
        self.page.on("dialog", lambda dialog: asyncio.create_task(dialog.accept()))

    async def _random_delay(self):
        """Add random delay to mimic human behavior."""
        delay = random.uniform(*self.delay_range)
        await asyncio.sleep(delay)

    async def _get_page_content(self, url: str, wait_for_selector: str = None, max_retries: int = 3) -> Optional[
        BeautifulSoup]:
        """
        Navigate to a URL and return BeautifulSoup object with retry logic.

        Args:
            url (str): URL to navigate to
            wait_for_selector (str): CSS selector to wait for before returning
            max_retries (int): Maximum number of retry attempts

        Returns:
            BeautifulSoup object or None if failed
        """
        for attempt in range(max_retries):
            try:
                logging.info(f"Navigating to: {url} (attempt {attempt + 1}/{max_retries})")

                # Clear any existing navigation
                try:
                    await self.page.evaluate("window.stop()")
                except:
                    pass

                # Navigate with multiple wait strategies
                response = await self.page.goto(
                    url,
                    wait_until='load',  # Wait for network to be idle
                    timeout=60000  # Longer timeout
                )

                if not response:
                    logging.warning(f"No response received for {url}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(5)
                        continue
                    return None

                # Check if we got blocked (common status codes for bot detection)
                if response.status in [403, 429, 503]:
                    logging.warning(f"Potential bot detection: Status {response.status}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(10)  # Longer delay for bot detection
                        continue
                    return None

                if response.status >= 400:
                    logging.error(f"HTTP error {response.status} for {url}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(3)
                        continue
                    return None

                # Wait for page to stabilize
                await asyncio.sleep(2)

                # Handle common overlays and pop-ups first
                await self._handle_overlays()

                # Wait for specific selector if provided
                if wait_for_selector:
                    try:
                        await self.page.wait_for_selector(wait_for_selector, timeout=15000)
                    except Exception as e:
                        logging.warning(f"Timeout waiting for selector {wait_for_selector}: {e}")
                        # Don't fail entirely if selector not found, page might still have content

                # Additional wait for dynamic content
                await self.page.wait_for_load_state('load', timeout=10000)

                # Random delay to mimic human browsing
                await self._random_delay()

                # Get page content
                content = await self.page.content()

                # Basic validation that we got actual content
                if len(content) < 1000:  # Suspiciously small page
                    logging.warning(f"Received suspiciously small content ({len(content)} chars)")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(5)
                        continue

                return BeautifulSoup(content, 'html.parser')

            except Exception as e:
                logging.error(f"Error fetching {url} (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    # Exponential backoff
                    wait_time = (2 ** attempt) + random.uniform(1, 3)
                    logging.info(f"Retrying in {wait_time:.1f} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    return None

    async def _handle_overlays(self):
        """Handle common pop-ups and overlays that might block content."""
        overlay_selectors = [
            'button[aria-label="Close"]',
            'button[data-testid="close-button"]',
            '.modal-close',
            '[data-testid="modal-close"]',
            'button:has-text("Close")',
            'button:has-text("No Thanks")',
            '[aria-label="Close dialog"]'
        ]

        for selector in overlay_selectors:
            try:
                # Check if overlay exists and is visible
                overlay = self.page.locator(selector)
                if await overlay.count() > 0 and await overlay.first.is_visible():
                    await overlay.first.click()
                    await asyncio.sleep(1)
                    break
            except Exception:
                continue

    async def search_appliances(self):
        """
        Extracts the most recent prices from the home depot website to update them in our db
        :return:
        """
        search_urls = {
            'DISHWASHER': 'https://www.homedepot.com/b/Appliances-Dishwashers/N-5yc1vZc3po?catStyle=ShowProducts',
            'DRYER': 'https://www.homedepot.com/b/Appliances-Washers-Dryers-Dryers-Gas-Dryers/N-5yc1vZc3o3',
            'STOVE': 'https://www.homedepot.com/b/Appliances-Ranges-Gas-Ranges/N-5yc1vZc3oy',
            'REFRIGERATOR': 'https://www.homedepot.com/b/Appliances-Refrigerators-Top-Freezer-Refrigerators/N-5yc1vZc3ns',
            'WASHER': 'https://www.homedepot.com/b/Appliances-Washers-Dryers-Washing-Machines-Top-Load-Washers/N-5yc1vZc3oc'
        }
        average_prices = {
            'DISHWASHER': 0,
            'DRYER': 0,
            'WASHER': 0,
            'STOVE': 0,
            'REFRIGERATOR': 0,
            'MICROWAVE': 0
        }
        for appliance_name, page_url in search_urls.items():
            try:

                # Wait for product grid to load with more generous timeout
                soup = await self._get_page_content(page_url, wait_for_selector='a[href*="/p/"]')
                if not soup:
                    logging.warning(f"Failed to load page {page_url}")
                    continue
                json_script = soup.find("script", {"type": "application/ld+json"})
                data = json.loads(json_script.string)
                if len(data) > 1:
                    products = data[1]["mainEntity"]["offers"]["itemOffered"]
                else:
                    products = data[0]["mainEntity"]["offers"]["itemOffered"]

                # Get first 5 prices
                prices = [p["offers"]["price"] for p in products[:5]]

                # Calculate average
                average_price = sum(prices) / len(prices)

                average_prices[appliance_name] = float(average_price)
                await asyncio.sleep(2)
            except Exception as e:
                logging.error(f'An issue occurred extracting the price of an appliance: {appliance_name}',
                              exc_info=True,
                              extra={'information': {'error': str(e)}})
                continue
        await self.close()

        return average_prices

    async def close(self):
        """Close the browser and clean up resources."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
