import logging
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR
from backend.db.model.query.sql_statements import (INSERT_CUSTOMER_PROPERTY_INTO_PROPERTY_TABLE,
                                                   INSERT_PROPERTY_STRUCTURES_INTO_STRUCTURES_TABLE,
                                                   INSERT_PROPERTY_APPLIANCES_INTO_APPLIANCE_TABLE)


class PropertyCreationInsertionService:
    def __init__(self, hp_ai_db_connection_pool):
        self.pool = hp_ai_db_connection_pool

    def insert_properties_into_db(self, user_id, property_creation_requests):
        """
        Wrapper method to insert property, appliances, and structures into their respective tables
        :param user_id: The internal id of a user inserting items into their table
        :param property_creation_requests: python list, a list of model objects
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        cnx = self.obtain_connection()
        property_data, properties = self.format_properties_for_table_insertion(
            user_id=user_id,
            property_creation_requests=property_creation_requests)
        insert_property_record_status, property_data = self.execute_insertion_statement_for_properties_table(
            cnx=cnx,
            property_data=property_data)
        insert_appliance_record_status, appliance_data = self.execute_insertion_statement_for_appliances_table(
            cnx=cnx,
            properties=properties)
        insert_structures_record_status, structure_data = self.execute_insertion_statement_for_structures_table(
            cnx=cnx,
            properties=properties)
        response = self.format_property_creation_response(
            insert_property_record_status=insert_property_record_status,
            insert_appliance_record_status=insert_appliance_record_status,
            insert_structures_record_status=insert_structures_record_status,
            property_data=property_data,
            appliance_data=appliance_data,
            structure_data=structure_data)
        cnx.close()
        logging.info(END_OF_METHOD)
        return response

    @staticmethod
    def execute_insertion_statement_for_properties_table(cnx, property_data):
        """
        Performs the actual insertion of a property into the property table
        :param cnx: The MySQLConnectionPool connection
        :param property_data: python tuple,
        :return:
        """
        logging.info(START_OF_METHOD)
        insert_property_record_status = 200
        try:
            cursor = cnx.cursor()
            cursor.executemany(INSERT_CUSTOMER_PROPERTY_INTO_PROPERTY_TABLE, property_data)
            cnx.commit()
            cursor.close()
        except Exception as e:
            logging.error('An issue occurred inserting a property into the property table',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            insert_property_record_status = 500
        logging.info(END_OF_METHOD)
        return insert_property_record_status, property_data

    @classmethod
    def execute_insertion_statement_for_appliances_table(cls, cnx, properties):
        """
        Inserts items into the appliance table
        :param cnx:
        :param properties:
        :return:
        """
        logging.info(START_OF_METHOD)
        insert_appliances_status = 200
        appliance_data = cls.format_appliances_for_table_insertion(properties=properties)
        try:
            cursor = cnx.cursor()
            cursor.executemany(INSERT_PROPERTY_APPLIANCES_INTO_APPLIANCE_TABLE, appliance_data)
            cnx.commit()
        except Exception as e:
            logging.error('An issue occurred inserting items into the appliance table',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            insert_appliances_status = 500
        logging.info(END_OF_METHOD)
        return insert_appliances_status

    @classmethod
    def execute_insertion_statement_for_structures_table(cls, cnx, properties):
        """
        Inserts items into the structures table
        :param cnx:
        :param properties:
        :return:
        """
        logging.info(START_OF_METHOD)
        insert_structures_status = 200
        structures_data = cls.format_structures_for_table_insertion(properties=properties)
        try:
            cursor = cnx.get_cursor()
            cursor.executemany(INSERT_PROPERTY_STRUCTURES_INTO_STRUCTURES_TABLE, structures_data)
            cnx.commit()
        except Exception as e:
            logging.error('An issue occurred inserting items into the structures table',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            insert_structures_status = 500
        logging.info(END_OF_METHOD)
        return insert_structures_status

    @staticmethod
    def format_property_creation_response(insert_property_record_status,
                                          insert_appliance_record_status,
                                          insert_structures_record_status,
                                          property_data,
                                          appliance_data,
                                          structure_data):
        """
        Formats the response for the /customers/properties route
        :param insert_property_record_status: python int, status of inserting record into properties table
        :param insert_appliance_record_status: python int, status of inserting record into appliance table
        :param insert_structures_record_status: python int, status of inserting record into structures table
        :param property_data: python dict, response of what was inserted into the properties table
        :param appliance_data: python dict, response of what was inserted into the appliance table
        :param structure_data: python dict, response of what was inserted into the structures table
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        response = {
            'propertyRecordStatus': insert_property_record_status,
            'applianceRecordStatus': insert_appliance_record_status,
            'applianceStructuresStatus': insert_structures_record_status,
            'propertiesTableResponse': property_data,
            'appliancesTableResponse': appliance_data,
            'structuresTableResponse': structure_data
        }
        logging.info(END_OF_METHOD)
        return response

    def obtain_connection(self):
        try:
            cnx = self.pool.get_connection()
            return cnx
        except Exception as e:
            logging.error('An issue occurred acquiring a connection to the pool',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)

    @staticmethod
    def format_properties_for_table_insertion(user_id, property_creation_requests):
        """
        Formates
        :param user_id:
        :param property_creation_requests:
        :return: python tuple
        """
        data = []
        properties = {}
        for property_id in range(1, len(property_creation_requests) + 1):
            entry = (user_id,
                     property_creation_requests[property_id].postal_code,
                     property_creation_requests[property_id].home_age,
                     property_creation_requests[property_id].home_address)
            data.append(entry)
            properties[property_id] = property_creation_requests[property_id]
        return data, properties


    @staticmethod
    def format_appliances_for_table_insertion(properties):
        """
        Formats the appliances to be able to execute an executemany statement
        :param properties
        :return: python list
        """
        data = []
        for property_id, property in properties.items():
            appliances = property.appliances
            for appliance_name, appliance_age in appliances.__dict__.items():
                entry = (property_id, appliance_name, appliance_age)
                data.append(entry)
        return data

    @staticmethod
    def format_structures_for_table_insertion(properties):
        """
        Formats the appliances to be able to execute an executemany statement
        :param properties
        :return: python list
        """
        data = []
        for property_id, property in properties.items():
            structures = property.structures
            for structure_name, structure_age in structures.__dict__.items():
                entry = (property_id, structure_name, structure_age)
                data.append(entry)
        return data
