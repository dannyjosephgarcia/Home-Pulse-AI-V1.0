import os

from dependency_injector import containers, providers
from backend.redfin_scraper.client.redfin_client import RedfinClient
from backend.db.client.hp_ai_db_connection_pool import HpAIDbConnectionPool
from backend.redfin_scraper.service.redfin_housing_data_extraction_service import RedfinHousingDataExtractionService
from backend.db.service.customer_creation_insertion_service import CustomerCreationInsertionService


class Container(containers.DeclarativeContainer):
    env = os.getenv('ENV')
    config = providers.Configuration(yaml_files=[f"./config-{env}.yaml"])

    redfin_client = providers.Singleton(RedfinClient,
                                        config.redfin.base_url,
                                        config.redfin.user_agent)

    redfin_housing_data_extraction_service = providers.Singleton(RedfinHousingDataExtractionService,
                                                                 redfin_client)

    home_pulse_db_connection_pool = providers.Singleton(HpAIDbConnectionPool,
                                                        config.home_pulse_ai_db.host,
                                                        config.home_pulse_ai_db.user,
                                                        config.home_pulse_ai_db.password,
                                                        config.home_pulse_ai_db.db)

    customer_creation_insertion_service = providers.Singleton(CustomerCreationInsertionService,
                                                              home_pulse_db_connection_pool)
