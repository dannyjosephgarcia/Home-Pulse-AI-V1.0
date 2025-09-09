import faiss
import pickle
import datetime
import logging
from common.logging.error.error import Error
from sentence_transformers import SentenceTransformer
from common.logging.error.error_messages import HOME_BOT_AI_ERROR
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD


class HomeBotAIService:
    def __init__(self, index_file_path, metadata_file_path, nearest_neighbors_threshold):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.nearest_neighbors_threshold = nearest_neighbors_threshold
        self.index_file_path = index_file_path
        self.metadata_file_path = metadata_file_path
        self.index_file = None
        self.metadata_file = None
        self._load_home_bot_ai_inference_files()

    def _load_home_bot_ai_inference_files(self):
        """
        Loads the appliances.index and metadata.pkl files at app startup
        """
        logging.info(START_OF_METHOD)
        try:
            index = faiss.read_index(self.index_file_path)
            with open(self.metadata_file_path, "rb") as f:
                metadata_file = pickle.load(f)
            self.index_file = index
            self.metadata_file = metadata_file
            logging.info(END_OF_METHOD)
        except Exception as e:
            logging.error('An issue occurred initializing home bot',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(HOME_BOT_AI_ERROR)

    def generate_lifecycle_query_answer(self, home_bot_question_model):
        """
        Answers a question sent by a user regarding the replacement date for an appliance
        :param home_bot_question_model: The model object storing data from the /ask route
        :return: python string
        """
        logging.info(START_OF_METHOD)
        try:
            query_text = home_bot_question_model.question
            query_vec = self.model.encode([query_text])
            distances, indices = self.index_file.search(query_vec, self.nearest_neighbors_threshold)
            best_distance = distances[0][0]
            logging.info(f'Here is the best distance: {best_distance}')
            record = self.metadata_file[indices[0][0]]
            brand = record['brand']
            appliance_model = record['model']
            average_life_span = record['avg_lifespan_years']
            current_date = datetime.datetime.today().date()
            time_diff = int(average_life_span) - int(home_bot_question_model.appliance_age)
            if time_diff <= 0:
                forecasted_replacement_date = current_date
            else:
                years = time_diff * 52
                forecasted_replacement_date = current_date + datetime.timedelta(weeks=years)
            prompt_data = {'brand': brand,
                           'appliance_model': appliance_model,
                           'average_life_span': average_life_span,
                           'forecasted_replacement_date': forecasted_replacement_date}
            logging.info(END_OF_METHOD)
            return prompt_data, average_life_span
        except Exception as e:
            logging.error('An issue occurred generating a response to the question',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            return "Sorry, I'm having trouble finding an answer to your question. Contact support because I'm an idiot!"

    @staticmethod
    def format_question_response(answer, prompt_data):
        """
        Formats the response from the route
        :param answer: The answer to the query sent by the user
        :param prompt_data:
        :return: python dict
        """
        logging.info(START_OF_METHOD)
        response = {'answer': answer,
                    'forecasted_replacement_date': prompt_data['forecasted_replacement_date']}
        logging.info(END_OF_METHOD)
        return response
