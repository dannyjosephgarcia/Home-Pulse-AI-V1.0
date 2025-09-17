import os
import stripe

from dependency_injector import containers, providers
from backend.db.client.hp_ai_db_connection_pool import HpAIDbConnectionPool
from backend.db.service.customer_creation_insertion_service import CustomerCreationInsertionService
from backend.db.service.property_creation_insertion_service import PropertyCreationInsertionService
from backend.db.service.customer_authentication_service import CustomerAuthenticationService
from backend.db.service.property_retrieval_service import PropertyRetrievalService
from backend.db.service.customer_profile_update_service import CustomerProfileUpdateService
from backend.payment.service.stripe_payment_session_creation_service import StripePaymentSessionCreationService
from backend.payment.service.update_payment_status_service import UpdatePaymentStatusService
from backend.db.service.tenant_information_retrieval_service import TenantInformationRetrievalService
from backend.db.service.tenant_information_update_service import TenantInformationUpdateService
from backend.db.service.tenant_information_insertion_service import TenantInformationInsertionService
from backend.data_harvesting.service.lowes_appliance_price_analysis_service import LowesAppliancePriceAnalysisService
from backend.data_harvesting.client.lowes_client import LowesClient
from backend.data_harvesting.client.sync_lowes_price_analysis_wrapper import SyncLowesPriceAnalysisWrapper
from backend.db.client.s3_client import S3Client
from backend.db.service.property_image_retrieval_service import PropertyImageRetrievalService
from backend.db.service.property_image_insertion_service import PropertyImageInsertionService
from backend.db.service.customer_subscription_deletion_service import CustomerSubscriptionDeletionService
from backend.home_bot_model.service.home_bot_ai_service import HomeBotAIService
from backend.db.service.customer_subscription_retrieval_service import CustomerSubscriptionRetrievalService
from backend.payment.service.stripe_payment_subscription_deletion_service import (
    StripePaymentSubscriptionDeletionService)
from backend.payment.service.delete_payment_status_service import DeletePaymentStatusService
from backend.db.service.forecasted_replacement_date_update_service import ForecastedReplacementDateUpdateService
from backend.home_bot_model.service.home_bot_llm_rag_service import HomeBotLLMRAGService
from backend.home_bot_model.client.sagemaker_client import SagemakerClient
from backend.db.service.appliance_information_update_service import ApplianceInformationUpdateService
from backend.db.service.structure_information_update_service import StructureInformationUpdateService
from backend.db.service.property_creation_bulk_insertion_service import PropertyCreationBulkInsertionService


class Container(containers.DeclarativeContainer):
    env = os.getenv('ENV')
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    config = providers.Configuration(yaml_files=[f"./backend/app/config-{env}.yaml"])

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

    tenant_information_retrieval_service = providers.Singleton(TenantInformationRetrievalService,
                                                               home_pulse_db_connection_pool)

    tenant_information_update_service = providers.Singleton(TenantInformationUpdateService,
                                                            home_pulse_db_connection_pool)

    tenant_information_insertion_service = providers.Singleton(TenantInformationInsertionService,
                                                               home_pulse_db_connection_pool,
                                                               tenant_information_retrieval_service)

    lowes_client = providers.Singleton(LowesClient,
                                       config.lowes.delay,
                                       config.lowes.user_agent,
                                       config.lowes.base_url)

    lowes_appliance_price_analysis_service = providers.Singleton(LowesAppliancePriceAnalysisService,
                                                                 home_pulse_db_connection_pool)

    sync_lowes_price_analysis_wrapper = providers.Singleton(SyncLowesPriceAnalysisWrapper,
                                                            lowes_client)

    s3_client = providers.Singleton(S3Client,
                                    config.aws.access_key_id,
                                    config.aws.secret_access_key,
                                    config.aws.region_name)

    sagemaker_client = providers.Singleton(SagemakerClient,
                                           config.aws.access_key_id,
                                           config.aws.secret_access_key,
                                           config.aws.region_name)

    property_image_retrieval_service = providers.Singleton(PropertyImageRetrievalService,
                                                           home_pulse_db_connection_pool,
                                                           s3_client,
                                                           config.aws.bucket_name)

    property_image_insertion_service = providers.Singleton(PropertyImageInsertionService,
                                                           home_pulse_db_connection_pool,
                                                           s3_client,
                                                           config.aws.bucket_name)

    stripe_subscription_deletion_service = providers.Singleton(StripePaymentSubscriptionDeletionService,
                                                               config.stripe.base_url,
                                                               config.stripe.secret_key)

    customer_subscription_deletion_service = providers.Singleton(CustomerSubscriptionDeletionService,
                                                                 home_pulse_db_connection_pool,
                                                                 stripe_subscription_deletion_service)

    delete_payment_status_service = providers.Singleton(DeletePaymentStatusService,
                                                        home_pulse_db_connection_pool,
                                                        config.stripe.webhook_secret_deletion)

    customer_subscription_retrieval_service = providers.Singleton(CustomerSubscriptionRetrievalService,
                                                                  home_pulse_db_connection_pool)

    home_bot_ai_service = providers.Singleton(HomeBotAIService,
                                              config.home_bot.index_file_path,
                                              config.home_bot.metadata_file_path,
                                              config.home_bot.neighbors_threshold)

    forecasted_replacement_date_update_service = providers.Singleton(ForecastedReplacementDateUpdateService,
                                                                     home_pulse_db_connection_pool)

    home_bot_rag_llm_service = providers.Singleton(HomeBotLLMRAGService,
                                                   sagemaker_client,
                                                   config.home_bot.llm_endpoint,
                                                   config.home_bot.prompt_string)

    appliance_information_update_service = providers.Singleton(ApplianceInformationUpdateService,
                                                               home_pulse_db_connection_pool)

    structure_information_update_service = providers.Singleton(StructureInformationUpdateService,
                                                               home_pulse_db_connection_pool)

    property_creation_bulk_insertion_service = providers.Singleton(PropertyCreationBulkInsertionService,
                                                                   home_pulse_db_connection_pool)
