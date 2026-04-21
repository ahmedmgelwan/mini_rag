from .. LLMInterface import LLMInterface
import cohere
import logging
from ..LLMEnums import CoHereEnums, DocumentTypeEnum


class CoHereProvider(LLMInterface):
    
    def __init__(self,
                 api_key: str,
                 base_url: str = None,
                 default_max_input_tokens: int = 1024,
                 default_max_output_tokens: int = 1024,
                 temperature: float = 0.1
                 ):
        self.api_key = api_key
        self.base_url = base_url
        self.default_max_input_tokens = default_max_input_tokens
        self.temperature = temperature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        self.enums = CoHereEnums
        self.client = cohere.Client(api_key = self.api_key)
        
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id


    def set_embedding_model(self,model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    
    def process_text(self, text: str):
        # Don't truncate here to preserve full context including question
        return text.strip()
    
    def generate_text(self, prompt: str, chat_history: list = [],
                       max_output_tokens: int= None, temperature: float=None):
        
        if not self.client:
            self.logger.error("CoHere client was not set")
            return None
        
        if not self.generation_model_id:
            self.logger.error('Generation model for CoHere was not set')
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_max_input_tokens
        temperature = temperature if temperature else self.temperature

        response = self.client.chat(
            model=self.generation_model_id,
            chat_history=chat_history,
            max_input_tokens=self.default_max_input_tokens,
            max_tokens=max_output_tokens,
            temperature=temperature,
            message=self.process_text(prompt)
        )
        if not response or not response.text:
            self.logger.error('Error while generating text with CoHere')
            return None
        
        return response.text
        

    def generate_embedding(self, text: str, document_type:str = None):
        if not self.client:
            self.logger.error('CoHere client was not set')
            return None
        
        if not self.embedding_model_id:
            self.logger.error('Embedding model for CoHere was not set')
            return None
        input_type = self.enums.DOCUMENT.value
        if document_type == DocumentTypeEnum.QUERY.value:
            input_type = self.enums.QUERY.value
        
        response = self.client.embed(
            model= self.embedding_model_id,
            texts= [self.process_text(text)],
            input_type=input_type,
            embedding_types=['float']
        )
        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error('Error while embedding text with CoHere') 
            return None
        return response.embeddings.float[0]
    def construct_prompt(self, prompt: str, role:str):
        return {
            'role': role,
            'text': self.process_text(prompt)
        }