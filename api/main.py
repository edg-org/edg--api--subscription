from fastapi import FastAPI

from api.configs.Environment import get_environment_variables
from api.metadata.Tags import Tags
from api.models.BaseModel import init
from api.routers.v1.InvestigateContactsRouter import InvestigateContactRouter
from api.routers.v1.ContactsRouter import ContactsRouter

# Application Environment Configuration
env = get_environment_variables()

# Core Application Instance
app = FastAPI(
    title=env.APP_NAME,
    version=env.API_VERSION,
    openapi_tags=Tags,
    root_path=env.API_ROOT_PATH,
)

# Add Routers
app.include_router(ContactsRouter)
app.include_router(InvestigateContactRouter)

# app.include_router(BookRouter)

# Initialise Data Model Attributes
init()