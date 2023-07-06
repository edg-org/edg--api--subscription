from typing import List
from fastapi import APIRouter, Depends, status
from api.configs.Environment import get_env_var
from api.subscription.services.ContractService import ContractService
from api.subscriber.schemas.ContactsSchema import (
    SearchByParams,
    ContactOutputDto, 
    ContactsInputDto,
    SearchAllContact, 
    ContactsInputUpdateDto,
    ContactDtoWithPagination
)
from api.subscriber.services.ContactsService import ContactsService
from api.subscription.schemas.ContractSchema import (
    ContractDto,
    InvoiceDetails,
    ContactContracts,
    ContractInvoiceParams,
    ContractInvoiceDetails
)
from api.subscription.utilis.JWTBearer import JWTBearer

env = get_env_var()
router_path = env.api_routers_prefix + env.api_version

contactRouter = APIRouter(
    prefix=router_path + "/customers",
    tags=["Customer"],
    dependencies=[Depends(JWTBearer())]
)

@contactRouter.post(
    "/",
    response_model=List[ContactOutputDto],
    summary="create contact",
    description="use this endpoint to create a new contact"
)
def create_contact(
        contact: List[ContactsInputDto],
        contact_service: ContactsService = Depends()
):
    return contact_service.create_contact(contact)


@contactRouter.put(
    "/{number}",
    response_model=ContactOutputDto,
    summary="update user by customer number",
    description="use this endpoint to update user infos"
)
def update_contact(
        number: str,
        contact: ContactsInputUpdateDto,
        contact_service: ContactsService = Depends()
):
    return contact_service.update_contact(number, contact)


@contactRouter.delete(
    "/{number}",
    summary="delete user by customer number",
    description="This will display info only for active account"
)
def delete_contact(
        number: str,
        contact_service: ContactsService = Depends()
):
    contact_service.delete_contact(number)


@contactRouter.get(
    "/search",
    response_model=ContactOutputDto,
    summary="Search customer by params",
    description=" This endpoint is use to search customer by given params (pid passport number or ID number"
                ", email, customer number and phone number, at least one param should be applied) return specific user"
)
async def search_contact_by_params(
        query_params: SearchByParams = Depends(),
        contact_service: ContactsService = Depends()
):
    return contact_service.search_contact_by_param(query_params)


@contactRouter.get(
    "",
    response_model=ContactDtoWithPagination,
    summary="search customer by given params",
    description="This will display info only for given params (type maybe client, abonne or prospect) return collection"
)
def get_contacts_for_client(
        offset: int = 0,
        limit: int = 10,
        type_contact: SearchAllContact = Depends(),
        contact_service: ContactsService = Depends()
):
    return contact_service.get_contacts_for_client(offset, limit, type_contact)


@contactRouter.get(
    path="/{number}/subscriptions",
    response_model=List[ContractDto],
    status_code=status.HTTP_200_OK,
    summary="This endpoint filter contract by contract unique number",
    description="This endpoint filter contract by contract unique number",
)
async def get_billing(
        number: str,
        contract_service: ContractService = Depends()
):
    return contract_service.get_contracts_by_contact_number(number)


@contactRouter.get(
    "/{number}/details",
    response_model=List[ContractInvoiceDetails],
    status_code=status.HTTP_200_OK,
    summary="This endpoint get contract details",
    description="This endpoint get contract details"
)
async def get_contract_details(
        number: str,
        params: ContractInvoiceParams = Depends(),
        contract_service: ContractService = Depends()
):
    return contract_service.get_contract_details(number, params)
