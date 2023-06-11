from os import getenv
from dotenv import load_dotenv
from functools import lru_cache
from pydantic import BaseSettings

load_dotenv()

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
    auth_domain_name: str = getenv("AUTH_DOMAIN_NAME")
    api_root_path: str = getenv("API_ROOT_PATH")

    class Config:
        runtime_env = getenv("ENV")
        env_file = (f".env.{runtime_env}" if runtime_env else ".env")
        env_file_encoding = "utf-8"

@lru_cache
def get_env_var():
    return __EnvironmentSettings()