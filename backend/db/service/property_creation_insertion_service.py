import logging
from common.logging.error.error import Error
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR
from backend.db.model.property_creation_request import PropertyCreationRequest
from backend.db.model.query.sql_statements import (INSERT_CUSTOMER_PROPERTY_INTO_PROPERTY_TABLE,
                                                   INSERT_PROPERTY_STRUCTURES_INTO_STRUCTURES_TABLE,
                                                   INSERT_PROPERTY_APPLIANCES_INTO_APPLIANCE_TABLE)


class PropertyCreationInsertionService:
    def __init__(self, hp_ai_db_connection_pool):
        self.pool = hp_ai_db_connection_pool.pool

    def insert_properties_into_db(self, user_id, property_creation_requests):
        """
        Wrapper method to insert property, appliances, and structures into their respective tables
        :param user_id: The internal id of a user inserting items into their table
        :param property_creation_requests: python list, a list of model objects
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        cnx = self.obtain_connection()
        insert_property_record_status, properties = self.execute_insertion_statement_for_properties_table(
            cnx=cnx,
            user_id=user_id,
            property_creation_requests=property_creation_requests)
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
            property_data=properties,
            appliance_data=appliance_data,
            structure_data=structure_data)
        cnx.close()
        logging.info(END_OF_METHOD)
        return response

    @staticmethod
    def execute_insertion_statement_for_properties_table(cnx, user_id, property_creation_requests):
        """
        Performs the actual insertion of a property into the property table
        :param cnx: The MySQLConnectionPool connection
        :param user_id
        :param property_creation_requests:
        :return:
        """
        logging.info(START_OF_METHOD)
        insert_property_record_status = 200
        properties = {}
        try:
            cursor = cnx.cursor()
            for i in range(len(property_creation_requests)):
                property_data = (user_id, property_creation_requests[i].postal_code,
                                 property_creation_requests[i].home_age, property_creation_requests[i].home_address)
                cursor.execute(INSERT_CUSTOMER_PROPERTY_INTO_PROPERTY_TABLE, property_data)
                cnx.commit()
                property_id = cursor.lastrowid
                properties[property_id] = property_creation_requests[i]
            cursor.close()
        except Exception as e:
            logging.error('An issue occurred inserting a property into the property table',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            insert_property_record_status = 500
            cnx.rollback()
        logging.info(END_OF_METHOD)
        return insert_property_record_status, properties

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
            cnx.rollback()
        logging.info(END_OF_METHOD)
        return insert_appliances_status, appliance_data

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
            cursor = cnx.cursor()
            cursor.executemany(INSERT_PROPERTY_STRUCTURES_INTO_STRUCTURES_TABLE, structures_data)
            cursor.close()
            cnx.commit()
        except Exception as e:
            logging.error('An issue occurred inserting items into the structures table',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            insert_structures_status = 500
            cnx.rollback()
        logging.info(END_OF_METHOD)
        return insert_structures_status, structures_data

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
        appliances = {}
        structures = {}
        for app in appliance_data:
            property_id = app[0]
            appliance_name = app[1]
            appliance_age = app[2]
            pairing = {appliance_name: appliance_age}
            if property_id in appliances:
                appliances[property_id].append(pairing)
            else:
                appliances[property_id] = [pairing]
        for struct in structure_data:
            property_id = struct[0]
            structure_name = struct[1]
            structure_age = struct[2]
            pairing = {structure_name: structure_age}
            if property_id in structures:
                structures[property_id].append(pairing)
            else:
                structures[property_id] = [pairing]
        response = {
            'propertyRecordStatus': insert_property_record_status,
            'applianceRecordStatus': insert_appliance_record_status,
            'applianceStructuresStatus': insert_structures_record_status,
            'appliancesTableResponse': appliances,
            'structuresTableResponse': structures
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

    @staticmethod
    def construct_property_creation_requests(user_id, request_json):
        """
        Method constructs a list of PropertyCreationRequest objects
        :param user_id: The internal identifier of the logged in user
        :param request_json: python dict, the request to the route
        :return: python list
        """
        logging.info(START_OF_METHOD)
        property_creation_requests = []
        size = len(request_json)
        if size > 0:
            for i in range(size):
                single_request = request_json[i]
                property_creation_request = PropertyCreationRequest(user_id, single_request)
                property_creation_requests.append(property_creation_request)
        logging.info(END_OF_METHOD)
        return property_creation_requests
