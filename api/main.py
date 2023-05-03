from fastapi import FastAPI

from api.configs.Environment import get_environment_variables
from api.metadata.Tags import Tags
from api.contact.models.BaseModel import init
from api.contact.routers.v1.InvestigateContactsRouter import InvestigateContactRouter
from api.contact.routers.v1.ContactsRouter import ContactsRouter
from api.subscriber_api.routers.InvestigateSubscriberContractRouter import InvestigateContractRouter
from api.subscriber_api.routers.SubscriberContractRouter import SubscriberContractAPIRouter

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
app.include_router(InvestigateContactRouter)
app.include_router(SubscriberContractAPIRouter)
app.include_router(InvestigateContractRouter)

# app.include_router(BookRouter)

# Initialise Data Model Attributes
init()









