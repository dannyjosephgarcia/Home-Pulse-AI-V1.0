import logging
import pandas as pd
from common.logging.error.error import Error
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR, INVALID_REQUEST, INVALID_BULK_CSV_FILE
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from backend.db.model.query.sql_statements import (
    INSERT_CUSTOMER_PROPERTY_INTO_PROPERTY_TABLE,
    INSERT_UNITS_INTO_UNITS_TABLE,
    INSERT_PROPERTY_APPLIANCES_INTO_APPLIANCE_TABLE,
    INSERT_PROPERTY_STRUCTURES_INTO_STRUCTURES_TABLE
)


class PropertyCreationBulkInsertionService:
    def __init__(self, hp_ai_db_connection_pool):
        self.pool = hp_ai_db_connection_pool.pool

    def bulk_upload_properties_into_db(self, bulk_insertion_request, user_id):
        """
        Uploads the contents of the CSV file into our database
        :param bulk_insertion_request: The model object responsible for storing our data
        :param user_id: The ID of the user uploading properties
        :return: python dict, the response for the route
        """
        logging.info(START_OF_METHOD)
        cnx = self.obtain_connection()
        bulk_properties_df = self.validate_contents_of_csv_file(
            content=bulk_insertion_request.content)
        data_to_upload = self.parse_csv_file_for_upload(
            bulk_properties_df=bulk_properties_df,
            user_id=user_id
        )
        insert_record_status = self.execute_bulk_properties_insertion(
            cnx=cnx,
            data_to_upload=data_to_upload)
        response = {'insertRecordStatus': insert_record_status}
        logging.info(END_OF_METHOD)
        return response

    @staticmethod
    def validate_contents_of_csv_file(content):
        """
        Parses the contents of the file to ensure the user uploaded the correct information
        :param content: The content of the CSV file
        """
        logging.info(START_OF_METHOD)
        try:
            bulk_properties_df = pd.read_csv(content)
            required_columns = [
                'street', 'city', 'state', 'postal_code', 'property_age', 'unit_number',
                'stove_brand', 'stove_model', 'stove_age',
                'washer_brand', 'washer_model', 'washer_age',
                'air_conditioner_brand', 'air_conditioner_model', 'air_conditioner_age',
                'water_heater_brand', 'water_heater_model', 'water_heater_age',
                'dryer_brand', 'dryer_model', 'dryer_age',
                'dishwasher_brand', 'dishwasher_model', 'dishwasher_age',
                'refrigerator_brand', 'refrigerator_model', 'refrigerator_age',
                'roof_age', 'driveway_age', 'furnace_age', 'deck_age'
            ]

            missing_columns = [col for col in required_columns if col not in bulk_properties_df.columns]
            if missing_columns:
                logging.error(f'CSV file is missing required columns: {missing_columns}')
                raise Error(INVALID_BULK_CSV_FILE)

            logging.info(END_OF_METHOD)
            return bulk_properties_df
        except Error:
            raise
        except Exception as e:
            logging.error('There was an issue parsing the CSV file',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INVALID_BULK_CSV_FILE)

    @staticmethod
    def parse_csv_file_for_upload(bulk_properties_df, user_id):
        """
        Parses the dataframe generated from the CSV file to upload to the database
        :param bulk_properties_df: The bulk property file
        :param user_id: The ID of the user uploading properties
        :return: python list of dicts containing property, unit, appliance, and structure data
        """
        logging.info(START_OF_METHOD)
        data_to_upload = []

        for row in bulk_properties_df.itertuples(index=False):
            def safe_int(value):
                if pd.isna(value) or value == '' or str(value).strip() == '':
                    return None
                try:
                    return int(value)
                except (ValueError, TypeError):
                    return None

            property_data = {
                'user_id': user_id,
                'street': str(row.street).strip(),
                'city': str(row.city).strip(),
                'state': str(row.state).strip(),
                'postal_code': str(row.postal_code).strip(),
                'property_age': safe_int(row.property_age),
                'unit_number': str(row.unit_number),
                'address': f"{row.street}, {row.city}, {row.state}"
            }

            appliances = []
            def safe_str(value):
                if pd.isna(value) or value == '' or str(value).strip() == '':
                    return None
                return str(value).strip()

            stove_age = safe_int(row.stove_age)
            stove_brand = safe_str(row.stove_brand)
            stove_model = safe_str(row.stove_model)
            if stove_age is not None and stove_brand is not None:
                appliances.append({
                    'appliance_type': 'stove',
                    'appliance_brand': stove_brand,
                    'appliance_model': stove_model,
                    'age_in_years': stove_age
                })

            washer_age = safe_int(row.washer_age)
            washer_brand = safe_str(row.washer_brand)
            washer_model = safe_str(row.washer_model)
            if washer_age is not None and washer_brand is not None:
                appliances.append({
                    'appliance_type': 'washer',
                    'appliance_brand': washer_brand,
                    'appliance_model': washer_model,
                    'age_in_years': washer_age
                })

            air_conditioner_age = safe_int(row.air_conditioner_age)
            air_conditioner_brand = safe_str(row.air_conditioner_brand)
            air_conditioner_model = safe_str(row.air_conditioner_model)
            if air_conditioner_age is not None and air_conditioner_brand is not None:
                appliances.append({
                    'appliance_type': 'air_conditioner',
                    'appliance_brand': air_conditioner_brand,
                    'appliance_model': air_conditioner_model,
                    'age_in_years': air_conditioner_age
                })

            water_heater_age = safe_int(row.water_heater_age)
            water_heater_brand = safe_str(row.water_heater_brand)
            water_heater_model = safe_str(row.water_heater_model)
            if water_heater_age is not None and water_heater_brand is not None:
                appliances.append({
                    'appliance_type': 'water_heater',
                    'appliance_brand': water_heater_brand,
                    'appliance_model': water_heater_model,
                    'age_in_years': water_heater_age
                })

            dryer_age = safe_int(row.dryer_age)
            dryer_brand = safe_str(row.dryer_brand)
            dryer_model = safe_str(row.dryer_model)
            if dryer_age is not None and dryer_brand is not None:
                appliances.append({
                    'appliance_type': 'dryer',
                    'appliance_brand': dryer_brand,
                    'appliance_model': dryer_model,
                    'age_in_years': dryer_age
                })

            dishwasher_age = safe_int(row.dishwasher_age)
            dishwasher_brand = safe_str(row.dishwasher_brand)
            dishwasher_model = safe_str(row.dishwasher_model)
            if dishwasher_age is not None and dishwasher_brand is not None:
                appliances.append({
                    'appliance_type': 'dishwasher',
                    'appliance_brand': dishwasher_brand,
                    'appliance_model': dishwasher_model,
                    'age_in_years': dishwasher_age
                })

            refrigerator_age = safe_int(row.refrigerator_age)
            refrigerator_brand = safe_str(row.refrigerator_brand)
            refrigerator_model = safe_str(row.refrigerator_model)
            if refrigerator_age is not None and refrigerator_brand is not None:
                appliances.append({
                    'appliance_type': 'refrigerator',
                    'appliance_brand': refrigerator_brand,
                    'appliance_model': refrigerator_model,
                    'age_in_years': refrigerator_age
                })

            structures = []
            roof_age = safe_int(row.roof_age)
            if roof_age is not None:
                structures.append({
                    'structure_type': 'roof',
                    'age_in_years': roof_age
                })

            driveway_age = safe_int(row.driveway_age)
            if driveway_age is not None:
                structures.append({
                    'structure_type': 'driveway',
                    'age_in_years': driveway_age
                })

            furnace_age = safe_int(row.furnace_age)
            if furnace_age is not None:
                structures.append({
                    'structure_type': 'furnace',
                    'age_in_years': furnace_age
                })

            deck_age = safe_int(row.deck_age)
            if deck_age is not None:
                structures.append({
                    'structure_type': 'deck',
                    'age_in_years': deck_age
                })

            data_to_upload.append({
                'property': property_data,
                'appliances': appliances,
                'structures': structures
            })

        logging.info(END_OF_METHOD)
        return data_to_upload

    @staticmethod
    def execute_bulk_properties_insertion(cnx, data_to_upload):
        """
        Uploads the file to our appliances and structures database
        :param cnx: The MySQLConnectionPool
        :param data_to_upload: The data to upload to the route
        :return: python int
        """
        logging.info(START_OF_METHOD)
        insert_record_status = 200
        try:
            cursor = cnx.cursor()
            for item in data_to_upload:
                property_data = item['property']
                appliances = item['appliances']
                structures = item['structures']

                property_params = (
                    property_data['user_id'],
                    property_data['street'],
                    property_data['city'],
                    property_data['state'],
                    property_data['postal_code'],
                    property_data['property_age'],
                    property_data['address']
                )
                cursor.execute(INSERT_CUSTOMER_PROPERTY_INTO_PROPERTY_TABLE, property_params)
                property_id = cursor.lastrowid

                unit_number = property_data['unit_number']
                unit_id = None

                if unit_number != str(-1):
                    unit_params = (property_id, unit_number)
                    cursor.execute(INSERT_UNITS_INTO_UNITS_TABLE, unit_params)
                    unit_id = cursor.lastrowid

                for appliance in appliances:
                    appliance_params = (
                        property_id,
                        unit_id,
                        appliance['appliance_type'],
                        appliance['appliance_brand'],
                        appliance['appliance_model'],
                        appliance['age_in_years'],
                        None
                    )
                    cursor.execute(INSERT_PROPERTY_APPLIANCES_INTO_APPLIANCE_TABLE, appliance_params)

                for structure in structures:
                    structure_params = (
                        property_id,
                        structure['structure_type'],
                        structure['age_in_years']
                    )
                    cursor.execute(INSERT_PROPERTY_STRUCTURES_INTO_STRUCTURES_TABLE, structure_params)

            cnx.commit()
            logging.info(f'Successfully inserted {len(data_to_upload)} properties with related data')
            logging.info(END_OF_METHOD)
            return insert_record_status

        except Exception as e:
            if cnx:
                cnx.rollback()
            logging.error('There was an issue bulk uploading to the table',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)

        finally:
            if cursor:
                cursor.close()

    def obtain_connection(self):
        try:
            cnx = self.pool.get_connection()
            return cnx
        except Exception as e:
            logging.error('An issue occurred acquiring a connection to the pool',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)
