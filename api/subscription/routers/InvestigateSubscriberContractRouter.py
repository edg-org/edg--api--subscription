from typing import Coroutine, Any, List

from fastapi import APIRouter, Depends, status

from api.subscription.schemas.SubscriberContractSchema import ContractDtoWithPagination, BillingDto, ContractDto
from api.subscription.services.SubscriberContractService import SubscriberContactService
from api.subscription.utilis.JWTBearer import JWTBearer

InvestigateContractRouter: APIRouter = APIRouter(
    prefix="/v1/customers",
    tags=["customer"],
    # dependencies=[Depends(JWTBearer())]
)


@InvestigateContractRouter.get(
    path="/{number}",
    response_model=ContractDtoWithPagination,
    status_code=status.HTTP_200_OK,
    summary="This endpoint filter contract by costume id",
    description="This endpoint filter contract by costume id",
)
async def get_contract_by_contact_number(
        number: str,
        page: int = 1,
        contract_service: SubscriberContactService = Depends()
):
    return contract_service.get_contract_by_contact_number(number, page)


@InvestigateContractRouter.get(
    path="/{number}/subscriptions",
    response_model=List[ContractDto],
    status_code=status.HTTP_200_OK,
    summary="This endpoint filter contract by contract unique number",
    description="This endpoint filter contract by contract unique number",
)
async def get_billing(
        number: str,
        contract_service: SubscriberContactService = Depends()
):
    return contract_service.get_contracts_by_contact_number(number)
