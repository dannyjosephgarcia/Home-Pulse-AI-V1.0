import asyncio


class SyncLowesPriceAnalysisWrapper:
    """Synchronous wrapper for the async scraper."""

    def __init__(self, lowes_client):
        self.lowes_client = lowes_client
        self.loop = None

    def __enter__(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.client = self.loop.run_until_complete(self.lowes_client.__aenter__())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            self.loop.run_until_complete(self.client.__aexit__(exc_type, exc_val, exc_tb))
        if self.loop:
            self.loop.close()

    def update_appliances(self):
        return self.loop.run_until_complete(self.client.search_appliances())

    # def scrape_product_page(self, product_url: str):
    #     return self.loop.run_until_complete(self.service.scrape_product_page())
    #
    # def get_product_by_model(self, model_number: str):
    #     return self.loop.run_until_complete(self.service.get_product_by_model())
