import os
import stripe

from dependency_injector import containers, providers
from backend.redfin_scraper.client.redfin_client import RedfinClient
from backend.db.client.hp_ai_db_connection_pool import HpAIDbConnectionPool
from backend.redfin_scraper.service.redfin_housing_data_extraction_service import RedfinHousingDataExtractionService
from backend.db.service.customer_creation_insertion_service import CustomerCreationInsertionService
from backend.db.service.property_creation_insertion_service import PropertyCreationInsertionService
from backend.db.service.customer_authentication_service import CustomerAuthenticationService
from backend.db.service.property_retrieval_service import PropertyRetrievalService
from backend.db.service.customer_profile_update_service import CustomerProfileUpdateService
from backend.payment.service.stripe_payment_session_creation_service import StripePaymentSessionCreationService
from backend.payment.service.update_payment_status_service import UpdatePaymentStatusService


class Container(containers.DeclarativeContainer):
    env = os.getenv('ENV')
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    config = providers.Configuration(yaml_files=[f"./backend/app/config-{env}.yaml"])

    redfin_client = providers.Singleton(RedfinClient,
                                        config.redfin.base_url,
                                        config.redfin.user_agent)

    redfin_housing_data_extraction_service = providers.Singleton(RedfinHousingDataExtractionService,
                                                                 redfin_client)

    home_pulse_db_connection_pool = providers.Singleton(HpAIDbConnectionPool,
                                                        config.home_pulse_ai_db.host,
                                                        config.home_pulse_ai_db.port,
                                                        config.home_pulse_ai_db.user,
                                                        config.home_pulse_ai_db.password,
                                                        config.home_pulse_ai_db.db)

    stripe_payment_session_creation_service = providers.Singleton(StripePaymentSessionCreationService,
                                                                  config.stripe.secret_key,
                                                                  config.stripe.success_url,
                                                                  config.stripe.cancel_url,
                                                                  config.stripe.price,
                                                                  config.stripe.mode,
                                                                  config.stripe.payment_type)

    customer_creation_insertion_service = providers.Singleton(CustomerCreationInsertionService,
                                                              home_pulse_db_connection_pool,
                                                              stripe_payment_session_creation_service)

    property_creation_insertion_service = providers.Singleton(PropertyCreationInsertionService,
                                                              home_pulse_db_connection_pool)

    property_retrieval_service = providers.Singleton(PropertyRetrievalService,
                                                     home_pulse_db_connection_pool)

    customer_authentication_service = providers.Singleton(CustomerAuthenticationService,
                                                          home_pulse_db_connection_pool,
                                                          config.security.secret_key)

    customer_profile_update_service = providers.Singleton(CustomerProfileUpdateService,
                                                          config.security.secret_key,
                                                          home_pulse_db_connection_pool)

    update_payment_status_service = providers.Singleton(UpdatePaymentStatusService,
                                                        home_pulse_db_connection_pool,
                                                        customer_authentication_service,
                                                        config.stripe.webhook_secret)
