import logging
from common.logging.error.error import Error
from mysql.connector.pooling import MySQLConnectionPool
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR


class HpAIDbConnectionPool:
    def __init__(self, host, user, password, db):
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.pool = self.start_hp_ai_db_pool()

    def start_hp_ai_db_pool(self):
        """
        Creates a MySQLConnectionPool instance at server startup
        :return: MySQLConnectionPool instance
        """
        logging.info(START_OF_METHOD)
        try:
            db_config = {
                'database': self.db,
                'host': self.host,
                'user': self.user,
                'password': self.password
            }
            pool = MySQLConnectionPool(pool_name='hp_ai_db_pool',
                                       **db_config)
            return pool
        except Exception as e:
            logging.error('An issue occurred establishing a connection pool to the database',
                          extra={'information': {'error': str(e)}},
                          exc_info=True)
            raise Error(INTERNAL_SERVICE_ERROR)
