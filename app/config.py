from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()  # put .env values into os.environ, so Langfuse and other libraries see them too

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Primary LLM (any OpenAI-compatible endpoint)
    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str = ""
    llm_model: str = "your-small-model"
    # Fallback LLM: a second provider or model, used if the primary keeps failing
    fallback_base_url: str = ""
    fallback_api_key: str = ""
    fallback_model: str = ""

    qdrant_url: str = "http://localhost:6333"
    rules_collection: str = "handling_rules"
    embed_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    top_k: int = 3


settings = Settings()
