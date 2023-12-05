from enum import Enum
from functools import cache
from pydantic_settings import BaseSettings


class GPTModel(str, Enum):
    gpt_4 = "gpt-4"
    gpt_3_5_turbo = "gpt-3.5-turbo"


class Settings(BaseSettings):
    service_name: str = "Cloud Project Generator"
    k_revision: str = "local"
    log_level: str = "DEBUG"
    # openai_key: str
    # model: GPTModel = GPTModel.gpt_3_5_turbo
    # telegram_token: str
    sentiment_model_id: str = "karina-aquino/spanish-sentiment-model"
    # api_url: str = "http://localhost:8000/"



    class Config:
        env_file = ".env"


@cache
def get_settings():
    return Settings()
