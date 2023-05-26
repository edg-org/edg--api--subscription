from typing import List
from fastapi import APIRouter, Depends, status, Query
from api.subscription.utilis.JWTBearer import JWTBearer
from api.subscription.services.SubscriberContractService import SubscriberContactService
from api.subscription.schemas.SubscriberContractSchema import (
    ContractDto,
    ContractDtoQueryParams,
    SubscriberContractSchema, 
    ContractDtoWithPagination,
    ContactDtoForBillingService, 
    ContactWithContractAndPricing,
    SubscriberContractInfoInputUpdate
)

env = get_environment_variables()
router_path = env.api_routers_prefix + env.api_version

SubscriberContractAPIRouter = APIRouter(
    prefix=router_path + "/subscriptions",
    tags=["Subscription"],
)

@SubscriberContractAPIRouter.post(
    "/",
    response_model=List[ContractDto],
    status_code=status.HTTP_201_CREATED,
    summary="This endpoint create a contract for contact",
    description="Using this endpoint, you will assign to contact a contract",

)
def create_contrat(
        contract_schema: List[SubscriberContractSchema],
        contract_service: SubscriberContactService = Depends()
):
    return contract_service.create_contract(contract_schema)


@SubscriberContractAPIRouter.put(
    path="/{number}",
    response_model=ContractDto,
    status_code=status.HTTP_200_OK,
    summary="This endpoint update a contract for contact",
    description="Using this endpoint, you will update the assigned contract for a specific contact",
)
def update_contract(
        number: str,
        contract_schema: SubscriberContractInfoInputUpdate,
        contract_service: SubscriberContactService = Depends()
):
    return contract_service.update_contract(number, contract_schema)


@SubscriberContractAPIRouter.delete(
    path="/{number}",
    response_model=ContractDto,
    status_code=status.HTTP_200_OK,
    summary="This endpoint is used to delete a contract for a given delivery point",
    description="Using this endpoint, you will resign the contract to the providing delivery point",

)
def delete_contract(
        number: str,
        contract_service: SubscriberContactService = Depends()
):
    return contract_service.delete_contract(number)

@SubscriberContractAPIRouter.get(
    "/search",
    response_model=ContractDtoWithPagination,
    status_code=status.HTTP_200_OK,
    summary="This endpoint filter contracts by the providing parameters",
    description="This endpoint filter contracts by the providing parameters",
)
async def get_contract_by_submitted_params(
        offset: int = 0,
        limit: int = 10,
        params: ContractDtoQueryParams = Depends(),
        contract_service: SubscriberContactService = Depends()
):
    return contract_service.get_contract_by_submitted_params(
        params,
        offset,
        limit
    )

# This endpoint will receive a list of contract_number and fetch information about contact and contracts
@SubscriberContractAPIRouter.get(
    path="/numbers/",
    status_code=status.HTTP_200_OK,
    response_model=ContactWithContractAndPricing,
    summary="This endpoint return the list of contract and their contact",
    description="This endpoint return the list of contract and their contact according to the providing contract number"
)
async def get_contract_and_contact_by_contract_uid(
        number: List[str] = Query(None),
        contract_service: SubscriberContactService = Depends()
):
    return contract_service.get_contract_and_contact_by_contract_uid(number)
