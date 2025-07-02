import os

from dependency_injector import containers, providers
from backend.redfin_scraper.client.redfin_client import RedfinClient
from backend.redfin_scraper.service.redfin_housing_data_extraction_service import RedfinHousingDataExtractionService


class Container(containers.DeclarativeContainer):
    env = os.getenv('ENV')
    config = providers.Configuration(yaml_files=[f"./config-{env}.yaml"])

    redfin_client = providers.Singleton(RedfinClient,
                                        config.redfin.base_url,
                                        config.redfin.user_agent)

    redfin_housing_data_extraction_service = providers.Singleton(RedfinHousingDataExtractionService,
                                                                 redfin_client)
