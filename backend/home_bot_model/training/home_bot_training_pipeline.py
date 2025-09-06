import os
import faiss
import pickle
import logging
import pandas as pd
from common.logging.error.error import Error
from sentence_transformers import SentenceTransformer
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error_messages import INTERNAL_SERVICE_ERROR
from backend.db.client.hp_ai_db_connection_pool import HpAIDbConnectionPool
from backend.db.model.query.sql_statements import SELECT_HOME_BOT_EMBEDDING_INFORMATION


class HomeBotTrainingPipeline:
    def __init__(self, hp_ai_db_connection_pool):
        self.pool = hp_ai_db_connection_pool.pool

    def generate_embeddings(self):
        """
        Leverages the home_bot_training_information
        :return:
        """
        logging.info(START_OF_METHOD)
        cnx = self.obtain_connection()
        df = pd.read_sql(SELECT_HOME_BOT_EMBEDDING_INFORMATION, cnx)
        cnx.close()

        model = SentenceTransformer('all-MiniLM-L6-v2')

        texts = df.apply(lambda row: f"{row['brand']} {row['model']} {row['category']}", axis=1)
        embeddings = model.encode(texts, convert_to_numpy=True)

        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)

        logging.info(f"Stored {index.ntotal} vectors in FAISS")

        faiss.write_index(index, "appliances.index")

        metadata = df.to_dict(orient="records")
        with open("metadata.pkl", "wb") as f:
            pickle.dump(metadata, f)
        logging.info(END_OF_METHOD)

    def obtain_connection(self):
        try:
            cnx = self.pool.get_connection()
            return cnx
        except Exception as e:
            logging.error('An issue occurred acquiring a connection to the pool',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(INTERNAL_SERVICE_ERROR)


if __name__ == "__main__":
    HOST = os.getenv('MYSQL_HOST')
    PORT = os.getenv('MYSQL_PORT')
    USER = os.getenv('MYSQL_USER')
    PASSWORD = os.getenv('MYSQL_PASS')
    DB = os.getenv('MYSQL_DB')
    cnx_pool = HpAIDbConnectionPool(HOST, PORT, USER, PASSWORD, DB)
    pipeline = HomeBotTrainingPipeline(cnx_pool)
    pipeline.generate_embeddings()
