from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    BOT_TOKEN: str
    DB_URL: str
    ADMIN_ID: int
    ADMIN_CHAT_ID: int
    ADMIN_USERNAME: str

    class Config:
        env_file = "secret.env"

config = Settings()