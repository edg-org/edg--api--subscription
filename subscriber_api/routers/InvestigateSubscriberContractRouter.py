from datetime import date

from fastapi import APIRouter, Depends, status

from subscriber_api.schemas.SubscriberContractSchema import ContractDto
from subscriber_api.services.SubscriberContractService import SubscriberContactService
from subscriber_api.utilis.JWTBearer import JWTBearer

InvestigateContractRouter: APIRouter = APIRouter(
    prefix="/v1/contracts/investigate",
    tags=["investigate contract"],
    dependencies=[Depends(JWTBearer)]
)


@InvestigateContractRouter.get(
    path="/{costume_id}",
    response_model=ContractDto,
    status_code=status.HTTP_200_OK,
    summary="This endpoint filter contract by costume id",
    description="This endpoint filter contract by costume id",
)
async def get_contract_by_customer_id_for_admin(
    costume_id: int,
    offset: int,
    limit: int,
    contract_service: SubscriberContactService = Depends()
):
    return contract_service.get_contract_by_customer_id_for_admin(costume_id, offset, limit)


@InvestigateContractRouter.get(
    path="/{contract_uid}",
    response_model=ContractDto,
    status_code=status.HTTP_200_OK,
    summary="This endpoint filter contract by contract unique number",
    description="This endpoint filter contract by contract unique number",
)
async def get_contract_by_contract_uid_for_admin(
       contract_uid: str,
       contract_service: SubscriberContactService = Depends()
):
    return contract_service.get_contract_by_contract_uid_for_admin(contract_uid)

