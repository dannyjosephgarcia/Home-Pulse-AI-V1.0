import json
import logging
import datetime
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD


class HomeBotLLMRAGService:
    def __init__(self, sagemaker_client, llm_endpoint, prompt_string):
        self.prompt_string = prompt_string
        self.llm_endpoint = llm_endpoint
        self.sagemaker_client = sagemaker_client.client

    def perform_rag_against_sagemaker_llm(self, query, prompt_data, appliance_age):
        """
        Calls model endpoint on Sagemaker to generate answer
        :param query: The question the user supplied
        :param prompt_data: The data found by are FAISS index
        :param appliance_age: The age of the appliance
        :return:
        """
        logging.info(START_OF_METHOD)
        try:
            final_query_string = self.construct_final_query_string(
                query=query,
                prompt_string=self.prompt_string,
                prompt_data=prompt_data,
                appliance_age=appliance_age)
            request = json.dumps({"inputs": final_query_string,
                                  "parameters": {
                                      "max_length": 300}})
            response = self.sagemaker_client.invoke_endpoint(
                EndpointName=self.llm_endpoint,
                ContentType='application/json',
                Body=request)
            result = response["Body"].read().decode("utf-8")
            result_json = json.loads(result)
            generated_text = result_json[0]['generated_text']
            cleaned_output = generated_text.replace("Assistant:", "").strip()
            logging.info(END_OF_METHOD)
            return cleaned_output
        except Exception as e:
            logging.error('An error occurred invoking the LLM model on SageMaker',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            return "Sorry, I'm having trouble answering that question right now. I'm an idiot!"

    @staticmethod
    def construct_final_query_string(query, prompt_string, prompt_data, appliance_age):
        """
        Performs the construction of the query string (helper method)
        :param query: The question the user supplied
        :param prompt_string: A configuration to give the tonality of the agent
        :param prompt_data: The data found by are FAISS index
        :param appliance_age: The age of the appliance
        :return: python str
        """
        logging.info(START_OF_METHOD)
        brand = prompt_data['brand']
        model = prompt_data['appliance_model']
        average_life_span = prompt_data['average_life_span']
        forecasted_replacement_date = datetime.datetime.strftime(prompt_data['forecasted_replacement_date'],
                                                                 '%Y-%m-%d')
        context_string = (f"A {brand} {model} lasts {int(average_life_span)} years; "
                          f"current model is {appliance_age} years old; "
                          f"replacement date is {forecasted_replacement_date}")
        few_shot_prompts = """
        User: When should I replace my fridge? 
        Assistant: Usually every 10–12 years, but yours should still be fine! 
        
        User: How long does a standard fridge last? 
        Assistant: Most fridges last about 10–12 years, so yours should still be fine! 
        
        User: How often should I replace my fridge? 
        Assistant: Typically, a fridge lasts for 10-12 years, so you shouldn't have to worry!"""
        user_assistant = few_shot_prompts + '\n' + f"User: {query}\n Answer in a conversational style: Please answer in a friendly, conversational way for the user"
        context_and_user_query = "Context summary: " + context_string + '\n' + user_assistant
        final_query_string = prompt_string + '\n' + context_and_user_query
        logging.info(END_OF_METHOD)
        return final_query_string
