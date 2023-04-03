from sqlalchemy.ext.declarative import declarative_base

from api.configs.Database import Engine

# Base Entity Model Schema
EntityMeta = declarative_base()


def init():
    EntityMeta.metadata.create_all(bind=Engine)
