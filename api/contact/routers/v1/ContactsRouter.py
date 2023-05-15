from typing import List

from fastapi import APIRouter, Depends, status

from api.contact.schemas.pydantic.ContactsSchema import ContactOutputDto, ContactsInputDto, ContactDtoWithPagination, \
    SearchByParams, SearchAllContact
from api.contact.services.ContactsService import ContactsService
from api.subscription.schemas.SubscriberContractSchema import ContractDto, InvoiceDetails, ContractInvoiceDetails, \
    ContractInvoiceParams, ContactContracts
from api.subscription.services.SubscriberContractService import SubscriberContactService

ContactsRouter = APIRouter(
    prefix="/v1/customers", tags=["customer"]
)


@ContactsRouter.post(
    "/",
    response_model=List[ContactOutputDto],
    summary="create user",
    description="use this endpoint to create a new user"
)
def create_contact(
        contact: List[ContactsInputDto],
        contact_service: ContactsService = Depends()
):
    return contact_service.create_contact(contact)


@ContactsRouter.put(
    "/{number}",
    response_model=ContactOutputDto,
    summary="update user by customer number",
    description="use this endpoint to update user infos"
)
def update_contact(
        number: str,
        contact: ContactsInputDto,
        contact_service: ContactsService = Depends()
):
    return contact_service.update_contact(number, contact)


@ContactsRouter.delete(
    "/{number}",
    summary="delete user by customer number",
    description="This will display info only for active account"
)
def delete_contact(
        number: str,
        contact_service: ContactsService = Depends()
):
    contact_service.delete_contact(number)


@ContactsRouter.get(
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


@ContactsRouter.get(
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


@ContactsRouter.get(
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


@ContactsRouter.get(
    "/{number}/details",
    response_model=List[ContractInvoiceDetails],
    status_code=status.HTTP_200_OK,
    summary="This endpoint get contract details",
    description="This endpoint get contract details"
)
async def get_contract_details(
        number: str,
        # contact: ContactContracts,
        params: ContractInvoiceParams = Depends(),
        contract_service: SubscriberContactService = Depends()
):
    return contract_service.get_contract_details(number,params)
