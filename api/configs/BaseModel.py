
from functools import lru_cache
from api.configs.Database import Engine
from sqlalchemy.ext.declarative import declarative_base

# Base Entity Model Schema
EntityMeta = declarative_base()

# create database function
@lru_cache()
def init():
    EntityMeta.metadata.create_all(bind=Engine)
