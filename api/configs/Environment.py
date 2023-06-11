from functools import lru_cache
import os

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class EnvironmentSettings(BaseSettings):
    API_VERSION: str = os.getenv("API_VERSION")
    APP_NAME: str = os.getenv("APP_NAME")
    DATABASE_DIALECT: str = os.getenv("DATABASE_DIALECT")
    DATABASE_HOSTNAME: str = os.getenv("DATABASE_HOSTNAME")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD")
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT"))
    DATABASE_USERNAME: str = os.getenv("DATABASE_USERNAME")
    API_ROOT_PATH: str = os.getenv("API_ROOT_PATH")
    DEBUG_MODE: bool = bool(os.getenv("DEBUG_MODE"))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_environment_variables():
    return EnvironmentSettings()