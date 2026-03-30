from .providers import OpenAIProvider
from .providers import CoHereProvider
from .LLMEnums import LLMProviders
from helpers import Settings

class LLMProviderFactory:
    def __init__(self, config: Settings):
        self.config = config
    
    def create(self, provider: str):
        if provider == LLMProviders.OPENAI.value:
            return OpenAIProvider(api_key = self.config.OPENAI_API_KEY,
                        base_url = self.config.OPENAI_BASE_URL,
                        defult_max_input_tokens = self.config.INPUT_DAFAULT_MAX_CHARACTERS,
                        defult_max_output_tokens = self.config.GENERATION_DAFAULT_MAX_TOKENS,
                        temprature = self.config.GENERATION_DAFAULT_TEMPERATURE)
        
        if provider == LLMProviders.COHERE.value:
            return CoHereProvider(api_key = self.config.COHERE_API_KEY,
                        defult_max_input_tokens = self.config.INPUT_DAFAULT_MAX_CHARACTERS,
                        defult_max_output_tokens = self.config.GENERATION_DAFAULT_MAX_TOKENS,
                        temprature = self.config.GENERATION_DAFAULT_TEMPERATURE)
        
        return None