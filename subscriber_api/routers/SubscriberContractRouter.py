from datetime import date
from typing import List

from fastapi import APIRouter, Depends, status, Form

from api.metadata.Tags import Tags
from subscriber_api.schemas.SubscriberContractSchema import ContractDto, \
    SubscriberContractSchema, ContractDtoIncoming, SubscriberContractInfoForFilter, Agency, AgencyIncomingFilter, \
    SubscriptionLevel, SubscriptionLevelIncomingFilter, ContractDtoForBillingMicroService, SubscriptionType

from subscriber_api.services.SubscriberContractService import SubscriberContactService
from subscriber_api.utilis.JWTBearer import JWTBearer

SubscriberContractAPIRouter: APIRouter = APIRouter(
    prefix="/v1/contracts",
    tags=["contract"],
    # dependencies=[Depends(JWTBearer)]
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
    path="/{contract_uid}",
    response_model=ContractDto,
    status_code=status.HTTP_200_OK,
    summary="This endpoint update a contract for contact",
    description="Using this endpoint, you will update the assigned contract for a specific contact",
)
def update_contract(
        contract_uid: str,
        contract_schema: SubscriberContractSchema,
        contract_service: SubscriberContactService = Depends()
):
    return contract_service.update_contract(contract_uid, contract_schema)


@SubscriberContractAPIRouter.put(
    path="contract-uid/{contract_uid}/status/{status_name}",
    response_model=ContractDto,
    status_code=status.HTTP_200_OK,
    summary="This endpoint update a contract for contact",
    description="Using this endpoint, you will update the assigned contract for a specific contact",
)
def update_contract_status(
        contract_uid: str,
        status_name: str,
        contract_service: SubscriberContactService = Depends()
):
    return contract_service.update_contract_status_by_contract_uid(contract_uid, status_name)


@SubscriberContractAPIRouter.put(
    path="contract-uid/{contract_uid}/previous-status/{previous_status}",
    response_model=ContractDto,
    status_code=status.HTTP_200_OK,
    summary="This endpoint update a contract for contact",
    description="Using this endpoint, you will update the assigned contract for a specific contact",
)
def update_contract_status(
        contract_uid: str,
        previous_status: str,
        contract_service: SubscriberContactService = Depends()
):
    return contract_service.update_contract_previous_status_by_contract_uid(contract_uid, previous_status)


@SubscriberContractAPIRouter.delete(
    path="/{delivery_point}",
    response_model=ContractDto,
    status_code=status.HTTP_200_OK,
    summary="This endpoint is used to delete a contract for a given delivery point",
    description="Using this endpoint, you will resign the contract to the providing delivery point",

)
def delete_contract(
        delivery_point: str,
        contract_service: SubscriberContactService = Depends()
):
    return contract_service.delete_contract(delivery_point)


@SubscriberContractAPIRouter.get(
    path="/{costume_id}",
    response_model=List[ContractDto],
    status_code=status.HTTP_200_OK,
    summary="This endpoint filter contract by costume id",
    description="This endpoint filter contract by costume id",
)
def get_contract_by_customer_id_for_client(
        costume_id: int,
        offset: int,
        limit: int,
        contract_service: SubscriberContactService = Depends()
):
    return contract_service.get_contract_by_customer_id_for_client(costume_id, offset, limit)


@SubscriberContractAPIRouter.get(
    path="/fill-billing/contract-uid",
    response_model=ContractDtoForBillingMicroService,
    status_code=status.HTTP_200_OK,
    summary="This endpoint filter contract by costume id",
    description="This endpoint filter contract by costume id",
)
def get_contract_by_contract_uid_for_microservice_billing(
        contract_uid: str,
        contract_service: SubscriberContactService = Depends()
):
    return contract_service.get_contract_by_contract_uid_for_microservice_billing(contract_uid)


@SubscriberContractAPIRouter.get(
    path="/contact-uid/{contract_uid}",
    response_model=ContractDto,
    status_code=status.HTTP_200_OK,
    summary="This endpoint filter contract by contract unique number",
    description="This endpoint filter contract by contract unique number",
)
async def get_contract_by_contract_uid_for_client(
        contract_uid: str,
        contract_service: SubscriberContactService = Depends()
):
    return contract_service.get_contract_by_contract_uid_for_client(contract_uid)


@SubscriberContractAPIRouter.get(
    path="/delivery-point/{delivery_point}",
    response_model=ContractDto,
    status_code=status.HTTP_200_OK,
    summary="This endpoint filter contract by contract unique number",
    description="This endpoint filter contract by contract unique number",
)
async def get_contract_by_contract_uid_for_client(
        delivery_point: str,
        contract_service: SubscriberContactService = Depends()
):
    return contract_service.get_contract_by_delivery_point(delivery_point)


@SubscriberContractAPIRouter.get(
    path="/contract-uid/{contract_uid}/contact-uid/{contact_uid}",
    response_model=ContractDto,
    status_code=status.HTTP_200_OK,
    summary="This endpoint filter contract by contract contract unique number and contact unique number",
    description="This endpoint filter contract by contract contract unique number and contact unique number",
)
async def get_contract_by_contact_uid_and_contract_uid_for_client(
        contract_uid: str,
        contact_uid: str,
        contract_service: SubscriberContactService = Depends()
):
    return contract_service.get_contract_by_contact_uid_and_contract_uid_for_client(contract_uid, contact_uid)


@SubscriberContractAPIRouter.get(
    path="/contract-uid/{contract_uid}/contact-pid/{contact_pid}",
    response_model=ContractDto,
    status_code=status.HTTP_200_OK,
    summary="This endpoint filter contract by contract unique number and contact identity unique number",
    description="This endpoint filter contract by contract unique and contact identity "
                "unique number(Passport number or ID number)",
)
async def get_contract_by_contact_pid_and_contract_uid_for_client(
        contract_uid: str,
        contact_pid: str,
        contract_service: SubscriberContactService = Depends()
):
    return contract_service.get_contract_by_contact_pid_and_contract_uid_for_client(contract_uid, contact_pid)


@SubscriberContractAPIRouter.get(
    "/params/a",
    response_model=List[ContractDto],
    status_code=status.HTTP_200_OK,
    summary="This endpoint filter contracts by the providing parameters",
    description="This endpoint filter contracts by the providing parameters",

)
async def get_contract_by_submitted_params(
        offset: int = 0,
        limit: int = 10,
        params: ContractDtoIncoming = Depends(),
        infos: SubscriberContractInfoForFilter = Depends(),
        agency: AgencyIncomingFilter = Depends(),
        contract_service: SubscriberContactService = Depends()
):
    return contract_service.get_contract_by_submitted_params(
        params,
        infos,
        agency,
        offset,
        limit
    )
