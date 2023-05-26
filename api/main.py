from fastapi import FastAPI

from api.contact.metadata.Tags import Tags
from api.contact.models.BaseModel import init
from api.configs.Environment import get_environment_variables
from api.contact.routers.v1.ContactsRouter import ContactsRouter
from api.subscription.routers.SubscriberContractRouter import SubscriberContractAPIRouter

# Application Environment Configuration
env = get_environment_variables()

# Core Application Instance
app = FastAPI(
    title=env.APP_NAME,
    version=env.API_VERSION,
    openapi_tags=Tags,
)

# Add Routers
app.include_router(ContactsRouter)
app.include_router(SubscriberContractAPIRouter)

# Initialise Data Model Attributes
init()




