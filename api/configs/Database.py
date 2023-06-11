from functools import lru_cache
from sqlalchemy import create_engine
from api.configs.Environment import get_env_var
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

# Runtime Environment Configuration
env = get_env_var()

Engine = create_engine(
    "{0}://{1}:{2}@{3}:{4}/{5}".format(
        env.database_dialect,
        env.database_username,
        env.database_password,
        env.database_hostname,
        env.database_port,
        env.database_name
    ),
    echo=get_env_var().debug_mode,
    future=True,
)

EntityMeta = declarative_base()
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=Engine
)

# Getting database function
def get_db_connection():
    db = scoped_session(SessionLocal)
    try:
        yield db
    finally:
        db.close()