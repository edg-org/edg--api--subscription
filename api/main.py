from fastapi import FastAPI

from api.configs.Environment import get_environment_variables
from api.metadata.Tags import Tags
from api.models.BaseModel import init
from api.routers.v1.AuthorRouter import AuthorRouter
from api.routers.v1.BookRouter import BookRouter

# Application Environment Configuration
env = get_environment_variables()

# Core Application Instance
app = FastAPI(
    title=env.APP_NAME,
    version=env.API_VERSION,
    openapi_tags=Tags,
)

# Add Routers
app.include_router(AuthorRouter)
app.include_router(BookRouter)

# Initialise Data Model Attributes
init()