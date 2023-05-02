import logging
import string
from typing import Callable

import fastapi
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.responses import RedirectResponse
from starlette import status

from subscriber_api.configs.Environment import get_environment_variables
from subscriber_api.metadata import Tags
from subscriber_api.models.BaseModel import init
from subscriber_api.routers import SubscriberContractRouter
from subscriber_api.routers.InvestigateSubscriberContractRouter import InvestigateContractRouter
from subscriber_api.routers.SubscriberContractRouter import SubscriberContractAPIRouter
from subscriber_api.utilis.JWTBearer import JWTBearer

env = get_environment_variables()
app = FastAPI(
    title=env.APP_NAME,
    version=env.API_VERSION,
    openapi_tags=Tags,
)


app.include_router(SubscriberContractAPIRouter)
app.include_router(InvestigateContractRouter)

# Initialise Data Model Attributes
init()
