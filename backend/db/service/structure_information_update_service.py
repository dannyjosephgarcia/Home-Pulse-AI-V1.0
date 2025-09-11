import logging
import datetime
from common.logging.error.error import Error
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR
from backend.db.model.query.sql_statements import UPDATE_STRUCTURE_INFORMATION_BULK


class StructureInformationUpdateService:
    def __init__(self, hp_ai_db_connection_pool):
        self.pool = hp_ai_db_connection_pool.pool

    def update_structure_information(self, structures_information_request):
        """
        Updates the structures within the structure_information table
        :param structures_information_request: The model object storing data from the request to the PUT route
        :return: python dict, the response
        """
        logging.info(START_OF_METHOD)
        cnx = self.obtain_connection()
        put_record_status = self.execute_update_statement_for_structures_table(
            cnx=cnx,
            property_id=structures_information_request.property_id,
            structure_updates=structures_information_request.structure_updates)
        response = {'putRecordStatus': put_record_status}
        logging.info(END_OF_METHOD)
        return response

    @classmethod
    def execute_update_statement_for_structures_table(cls, cnx, property_id, structure_updates):
        """
        Updates structure information within the structures table
        :param cnx: The MySQLConnectionPool Object
        :param property_id: The internal identifier of a property in our system
        :param structure_updates: The model object storing data for the PUT route
        :return: python int
        """
        logging.info(START_OF_METHOD)
        put_record_status = 200
        try:
            update_execute_many_data = cls.construct_execute_many_structure_object(
                property_id=property_id,
                structures_updates=structure_updates)
            cursor = cnx.cursor()
            cursor.executemany(UPDATE_STRUCTURE_INFORMATION_BULK, update_execute_many_data)
            cnx.commit()
            cursor.close()
            logging.info(END_OF_METHOD)
            return put_record_status
        except Exception as e:
            logging.error('There was an issue updating the appliances in the appliance table',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            return 500

    @staticmethod
    def construct_execute_many_structure_object(property_id, structures_updates):
        """
        Creates the list of data being requested to be updated
        :param property_id: The internal id of a property in our system
        :param structures_updates: The requested structure updates
        :return: python list
        """
        logging.info(START_OF_METHOD)
        items = []
        for structure in structures_updates:
            appliance_type = structure['structure_type']
            age_in_years = structure['age_in_years']
            estimated_replacement_cost = structure['estimated_replacement_cost']
            forecasted_replacement_date = datetime.datetime.strptime(structure['forecasted_replacement_date'],
                                                                     '%Y-%m-%d')
            data = (age_in_years, estimated_replacement_cost, forecasted_replacement_date, property_id, appliance_type)
            items.append(data)
        logging.info(END_OF_METHOD)
        return items

    def obtain_connection(self):
        try:
            cnx = self.pool.get_connection()
            return cnx
        except Exception as e:
            logging.error('An issue occurred acquiring a connection to the pool',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)