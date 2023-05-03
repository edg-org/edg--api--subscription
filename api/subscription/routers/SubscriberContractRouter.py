from typing import List

from fastapi import APIRouter, Depends, status

from api.subscription.schemas.SubscriberContractSchema import ContractDto, \
    SubscriberContractSchema, ContractDtoIncoming, ContractDtoWithPagination, BillingDto

from api.subscription.services.SubscriberContractService import SubscriberContactService
from api.subscription.utilis.JWTBearer import JWTBearer

SubscriberContractAPIRouter: APIRouter = APIRouter(
    prefix="/v1/subscriptions",
    tags=["contract"],
    # dependencies=[Depends(JWTBearer())]
)


@SubscriberContractAPIRouter.post(
    "/",
    response_model=List[ContractDto],
    # response_class=ContractDto,
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
        contract_schema: SubscriberContractSchema,
        contract_service: SubscriberContactService = Depends()
):
    return contract_service.update_contract(number, contract_schema)


@SubscriberContractAPIRouter.put(
    path="/{number}/activate",
    response_model=ContractDto,
    status_code=status.HTTP_200_OK,
    summary="This endpoint update a contract for contact",
    description="Using this endpoint, you will update the assigned contract for a specific contact",
)
def update_contract_status(
        number: str,
        contract_service: SubscriberContactService = Depends()
):
    return contract_service.activate_contract(number)


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
        page: int = 1,
        params: ContractDtoIncoming = Depends(),
        contract_service: SubscriberContactService = Depends()
):
    return contract_service.get_contract_by_submitted_params(
        params,
        page
    )


@SubscriberContractAPIRouter.get(
    path="/{number}",
    response_model=ContractDto,
    status_code=status.HTTP_200_OK,
    summary="This endpoint filter contract by contract unique number",
    description="This endpoint filter contract by contract unique number",
)
async def get_contract_by_contract_uid(
        number: str,
        contract_service: SubscriberContactService = Depends()
):
    return contract_service.get_contract_by_contract_uid(number)


@SubscriberContractAPIRouter.get(
    path="/{number}/invoicinginfos",
    response_model=BillingDto,
    status_code=status.HTTP_200_OK,
    summary="This endpoint filter contract by contract unique number",
    description="This endpoint filter contract by contract unique number",
)
async def get_contract_by_contract_uid_for_client(
        number: str,
        contract_service: SubscriberContactService = Depends()
):
    return contract_service.get_billing(number)

