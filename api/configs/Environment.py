
from os import getenv
from dotenv import load_dotenv
from functools import lru_cache
from pydantic import BaseSettings    
    
class __EnvironmentSettings(BaseSettings):
    app_name: str = getenv("APP_NAME")
    app_desc: str = getenv("APP_DESC")
    api_version: str = getenv("API_VERSION")
    database_dialect: str = getenv("DATABASE_DIALECT")
    database_hostname: str = getenv("DATABASE_HOSTNAME")
    database_username: str = getenv("DATABASE_USERNAME")
    database_password: str = getenv("DATABASE_PASSWORD")
    database_name: str = getenv("DATABASE_NAME")
    database_port: int = int(getenv("DATABASE_PORT"))
    api_routers_prefix: str = getenv("API_ROUTERS_PREFIX")
    debug_mode: bool = bool(getenv("DEBUG_MODE"))
    domaine_name: str = getenv("DOMAINE_NAME")

    class Config:
        env_file = get_env_filename()
        env_file_encoding = "utf-8"

@lru_cache
def get_environment_variables():
    return __EnvironmentSettings()
