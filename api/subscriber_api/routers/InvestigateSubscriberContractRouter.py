from fastapi import APIRouter, Depends, status

from api.subscriber_api.schemas.SubscriberContractSchema import ContractDtoWithPagination
from api.subscriber_api.services.SubscriberContractService import SubscriberContactService
from api.subscriber_api.utilis.JWTBearer import JWTBearer

InvestigateContractRouter: APIRouter = APIRouter(
    prefix="/v1/customers",
    tags=["customer"],
    dependencies=[Depends(JWTBearer)]
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
    response_model=ContractDtoWithPagination,
    status_code=status.HTTP_200_OK,
    summary="This endpoint filter contract by contract unique number",
    description="This endpoint filter contract by contract unique number",
)
async def get_contract_by_contract_uid_for_admin(
       contract_uid: str,
        page: int = 1,
       contract_service: SubscriberContactService = Depends()
):
    return contract_service.get_contract_by_contact_number(contract_uid, page)

