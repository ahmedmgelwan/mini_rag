from enum import Enum

class LLMProviders(Enum):
    OPENAI = 'OPENAI'
    COHERE = 'COHERE'

class OpenAIEnums(Enum):
    USER = 'user'
    SYSTEM = 'system'
    ASSISTANT = 'assistant'

class CoHereEnums(Enum):
    USER = 'USER'
    SYSTEM = 'SYSTEM'
    ASSISTANT = 'CHATBOT'
    DOCUMENT = 'search_document'
    QUERY = 'search_query'

class DocumentTypeEnum(Enum):
    DOCUMENT = 'document'
    QUERY = 'query'

