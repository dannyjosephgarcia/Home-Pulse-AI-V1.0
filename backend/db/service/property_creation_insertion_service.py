import logging
from common.logging.error.error import Error
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR
from backend.db.model.property_creation_request import PropertyCreationRequest
from backend.db.model.query.sql_statements import (INSERT_CUSTOMER_PROPERTY_INTO_PROPERTY_TABLE,
                                                   INSERT_PROPERTY_STRUCTURES_INTO_STRUCTURES_TABLE,
                                                   INSERT_PROPERTY_APPLIANCES_INTO_APPLIANCE_TABLE,
                                                   INSERT_UNITS_INTO_UNITS_TABLE,
                                                   SELECT_APPLIANCE_INFORMATION_FOR_REPLACEMENT_COST)


class PropertyCreationInsertionService:
    def __init__(self, hp_ai_db_connection_pool):
        self.pool = hp_ai_db_connection_pool.pool

    def insert_properties_into_db(self, user_id, property_creation_requests):
        """
        Wrapper method to insert property, units, appliances, and structures into their respective tables
        :param user_id: The internal id of a user inserting items into their table
        :param property_creation_requests: python list, a list of PropertyCreationRequest objects
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        cnx = self.obtain_connection()

        # Step 1: Insert properties
        insert_property_record_status, properties = self.execute_insertion_statement_for_properties_table(
            cnx=cnx,
            user_id=user_id,
            property_creation_requests=property_creation_requests)

        # Step 2: Insert units for multifamily properties and get unit_id mappings
        insert_units_status, unit_id_mappings = self.execute_insertion_statement_for_units_table(
            cnx=cnx,
            properties=properties)

        # Step 3: Get appliance replacement costs
        appliance_replacement_cost = self.execute_retrieval_statement_for_replacement_cost(
            cnx=cnx)

        # Step 4: Insert appliances (handles both property-level and unit-level)
        insert_appliance_record_status, appliance_data = self.execute_insertion_statement_for_appliances_table(
            cnx=cnx,
            properties=properties,
            unit_id_mappings=unit_id_mappings,
            appliance_replacement_cost=appliance_replacement_cost)

        # Step 5: Insert structures (always property-level, unit_id = NULL)
        insert_structures_record_status, structure_data = self.execute_insertion_statement_for_structures_table(
            cnx=cnx,
            properties=properties)

        # Step 6: Format response
        response = self.format_property_creation_response(
            insert_property_record_status=insert_property_record_status,
            insert_appliance_record_status=insert_appliance_record_status,
            insert_structures_record_status=insert_structures_record_status,
            insert_units_status=insert_units_status,
            property_data=properties,
            appliance_data=appliance_data,
            structure_data=structure_data)

        cnx.close()
        logging.info(END_OF_METHOD)
        return response

    @staticmethod
    def execute_retrieval_statement_for_replacement_cost(cnx):
        """
        Fetches the scraped average price of all appliances
        :param cnx: The MySQLConnectionPool connection
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        try:
            cursor = cnx.cursor()
            cursor.execute(SELECT_APPLIANCE_INFORMATION_FOR_REPLACEMENT_COST)
            table = cursor.fetchall()
            cursor.close()
            appliance_replacement_cost = {}
            for i in range(len(table)):
                appliance_replacement_cost[table[i][0]] = float(table[i][1])
            logging.info(END_OF_METHOD)
            return appliance_replacement_cost
        except Exception as e:
            logging.error('An issue occurred extracting the average appliance price',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)

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
                property_data = (user_id, property_creation_requests[i].street, property_creation_requests[i].city,
                                 property_creation_requests[i].state, property_creation_requests[i].zip,
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
    def execute_insertion_statement_for_units_table(cls, cnx, properties):
        """
        Inserts units into the units table for multifamily properties
        Returns a mapping of (property_id, unit_number) -> unit_id
        :param cnx: The MySQLConnectionPool connection
        :param properties: dict of property_id -> PropertyCreationRequest
        :return: tuple (status_code, unit_id_mappings dict)
        """
        logging.info(START_OF_METHOD)
        insert_units_status = 200
        unit_id_mappings = {}  # {(property_id, unit_number): unit_id}

        try:
            cursor = cnx.cursor()

            for property_id, property in properties.items():
                # Only process multifamily properties
                if not property.is_multifamily or not property.units:
                    continue

                for unit in property.units:
                    unit_data = (property_id, unit.unit_number)
                    cursor.execute(INSERT_UNITS_INTO_UNITS_TABLE, unit_data)
                    cnx.commit()
                    unit_id = cursor.lastrowid

                    # Store mapping
                    unit_id_mappings[(property_id, unit.unit_number)] = unit_id

            cursor.close()
        except Exception as e:
            logging.error('An issue occurred inserting units into the units table',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            insert_units_status = 500
            cnx.rollback()

        logging.info(END_OF_METHOD)
        return insert_units_status, unit_id_mappings

    @classmethod
    def execute_insertion_statement_for_appliances_table(cls, cnx, properties, unit_id_mappings, appliance_replacement_cost):
        """
        Inserts items into the appliance table
        Handles both property-level (single-family) and unit-level (multifamily) appliances
        :param cnx: MySQL connection
        :param properties: dict of property_id -> PropertyCreationRequest
        :param unit_id_mappings: dict of (property_id, unit_number) -> unit_id
        :param appliance_replacement_cost: dict of appliance prices
        :return: tuple (status_code, appliance_data list)
        """
        logging.info(START_OF_METHOD)
        insert_appliances_status = 200
        appliance_data = cls.format_appliances_for_table_insertion(
            properties=properties,
            unit_id_mappings=unit_id_mappings,
            appliance_replacement_cost=appliance_replacement_cost)
        try:
            cursor = cnx.cursor()
            cursor.executemany(INSERT_PROPERTY_APPLIANCES_INTO_APPLIANCE_TABLE, appliance_data)
            cnx.commit()
            cursor.close()
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
                                          insert_units_status,
                                          property_data,
                                          appliance_data,
                                          structure_data):
        """
        Formats the response for the /customers/properties route
        :param insert_property_record_status: python int, status of inserting record into properties table
        :param insert_appliance_record_status: python int, status of inserting record into appliance table
        :param insert_structures_record_status: python int, status of inserting record into structures table
        :param insert_units_status: python int, status of inserting record into units table
        :param property_data: python dict, response of what was inserted into the properties table
        :param appliance_data: python list, response of what was inserted into the appliance table
        :param structure_data: python list, response of what was inserted into the structures table
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        appliances = {}
        structures = {}

        # Format appliances: now includes unit_id at index 1
        for app in appliance_data:
            property_id = app[0]
            unit_id = app[1]  # May be None for single-family
            appliance_name = app[2]
            appliance_age = app[5]  # Index shifted due to unit_id
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
            'unitsRecordStatus': insert_units_status,
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
    def format_appliances_for_table_insertion(properties, unit_id_mappings, appliance_replacement_cost):
        """
        Formats the appliances to be able to execute an executemany statement
        Handles both property-level (single-family) and unit-level (multifamily) appliances
        :param properties: dict of property_id -> PropertyCreationRequest
        :param unit_id_mappings: dict of (property_id, unit_number) -> unit_id
        :param appliance_replacement_cost: dict of appliance prices
        :return: python list of tuples for insertion
        """
        data = []

        # Appliance prices
        dishwasher_price = appliance_replacement_cost.get('DISHWASHER', 100.00)
        dryer_price = appliance_replacement_cost.get('DRYER', 100.00)
        stove_price = appliance_replacement_cost.get('STOVE', 100.00)
        refrigerator_price = appliance_replacement_cost.get('REFRIGERATOR', 100.00)
        washer_price = appliance_replacement_cost.get('WASHER', 100.00)
        ac_unit_price = appliance_replacement_cost.get('AC_UNIT', 100.00)
        water_heater_price = appliance_replacement_cost.get('WATER_HEATER', 100.00)

        # Mapping of appliance names to their brand/model attribute names
        brand_model_map = {
            'stove': ('stove_brand', 'stove_model'),
            'dishwasher': ('dishwasher_brand', 'dishwasher_model'),
            'dryer': ('dryer_brand', 'dryer_model'),
            'refrigerator': ('refrigerator_brand', 'refrigerator_model'),
            'washer': ('washer_brand', 'washer_model'),
            'ac_unit': ('ac_unit_brand', 'ac_unit_model'),
            'water_heater': ('water_heater_brand', 'water_heater_model')
        }

        # Mapping of appliance names to their replacement costs
        price_map = {
            'stove': stove_price,
            'dishwasher': dishwasher_price,
            'dryer': dryer_price,
            'refrigerator': refrigerator_price,
            'washer': washer_price,
            'ac_unit': ac_unit_price,
            'water_heater': water_heater_price
        }

        for property_id, property in properties.items():
            if property.is_multifamily and property.units:
                # Multifamily: iterate through units and their appliances
                for unit in property.units:
                    # Get unit_id from mappings
                    unit_id = unit_id_mappings.get((property_id, unit.unit_number))

                    if unit_id is None:
                        logging.warning(f'No unit_id found for property {property_id}, unit {unit.unit_number}')
                        continue

                    # Process appliances for this unit
                    appliances = unit.appliances
                    for appliance_name, appliance_age in appliances.__dict__.items():
                        # Skip brand and model attributes
                        if appliance_name.endswith('_brand') or appliance_name.endswith('_model'):
                            continue

                        # Skip appliances that are None (not provided)
                        if appliance_age is None:
                            continue

                        brand = None
                        model = None

                        # Get brand and model if they exist
                        if appliance_name in brand_model_map:
                            brand_attr, model_attr = brand_model_map[appliance_name]
                            brand = getattr(appliances, brand_attr, None)
                            model = getattr(appliances, model_attr, None)

                        # Get replacement cost
                        replacement_cost = price_map.get(appliance_name, 100.00)

                        # Build entry: (property_id, unit_id, appliance_type, brand, model, age, cost)
                        entry = (property_id, unit_id, appliance_name, brand, model, appliance_age, replacement_cost)
                        data.append(entry)

            else:
                # Single-family: property-level appliances (unit_id = NULL)
                if property.appliances is None:
                    continue

                appliances = property.appliances
                for appliance_name, appliance_age in appliances.__dict__.items():
                    # Skip brand and model attributes
                    if appliance_name.endswith('_brand') or appliance_name.endswith('_model'):
                        continue

                    # Skip appliances that are None (not provided)
                    if appliance_age is None:
                        continue

                    brand = None
                    model = None

                    # Get brand and model if they exist
                    if appliance_name in brand_model_map:
                        brand_attr, model_attr = brand_model_map[appliance_name]
                        brand = getattr(appliances, brand_attr, None)
                        model = getattr(appliances, model_attr, None)

                    # Get replacement cost
                    replacement_cost = price_map.get(appliance_name, 100.00)

                    # Build entry: (property_id, NULL, appliance_type, brand, model, age, cost)
                    entry = (property_id, None, appliance_name, brand, model, appliance_age, replacement_cost)
                    data.append(entry)

        return data

    @staticmethod
    def format_structures_for_table_insertion(properties):
        """
        Formats the structures to be able to execute an executemany statement
        Handles optional structures - only inserts structures that are present
        :param properties
        :return: python list
        """
        data = []
        for property_id, property in properties.items():
            structures = property.structures
            for structure_name, structure_age in structures.__dict__.items():
                # Skip structures that are None (not provided)
                if structure_age is None:
                    continue

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
