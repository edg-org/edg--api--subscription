from fastapi import FastAPI
from api.metadata.Tags import Tags
from api.configs.BaseModel import init
from api.configs.Environment import get_env_var
from api.subscriber.routers.v1.ContactRouter import contactRouter
from api.subscription.routers.ContractRouter import contractRouter


# Application Environment Configuration
env = get_env_var()

# Core Application Instance
app = FastAPI(
    title=env.app_name,
    description=env.app_desc,
    version="0.0." + env.api_version,
    openapi_tags=Tags,
    root_path=env.api_root_path,
)

# Add Routers
app.include_router(contactRouter)
app.include_router(contractRouter)

# Initialise Data Model Attributes
init()
