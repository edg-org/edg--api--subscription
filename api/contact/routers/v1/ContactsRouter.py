from typing import List

from fastapi import APIRouter, Depends

from api.contact.schemas.pydantic.ContactsSchema import ContactOutputDto, ContactsInputDto, ContactDtoWithPagination
from api.contact.services.ContactsService import ContactsService

ContactsRouter = APIRouter(
    prefix="/v1/contacts", tags=["contacts"]
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
    "/{pid}",
    response_model=ContactOutputDto,
    summary="update user by pid",
    description="use this endpoint to update user infos"
)
def update_contact(
        pid: str,
        contact: ContactsInputDto,
        contact_service: ContactsService = Depends()
):
    return contact_service.update_contact(pid, contact)


@ContactsRouter.delete(
    "/{pid}",
    summary="delete user by pid",
    description="This will display info only for active account"
)
def delete_contact(
        pid: str,
        contact_service: ContactsService = Depends()
):
    contact_service.delete_contact(pid)


@ContactsRouter.get(
    "/phone",
    response_model=ContactOutputDto,
    summary="search user by phone only for active account",
    description="This will display info only for active account"
)
def get_contact_by_phone_for_client(
        phone: str,
        contact_service: ContactsService = Depends()):
    return contact_service.get_contact_by_phone_for_client(phone)


@ContactsRouter.get(
    "/email",
    response_model=ContactOutputDto,
    summary="search user by email only for active account",
    description="This will display info only for active account"
)
def get_contact_by_email_for_client(
        email: str,
        contact_service: ContactsService = Depends()):
    return contact_service.get_contact_by_email_for_client(email)


@ContactsRouter.get(
    "",
    response_model=ContactDtoWithPagination,
    summary="search users for active account",
    description="This will display info only for active account"
)
def get_contacts_for_client(
        page: int,
        contact_service: ContactsService = Depends()
):
    return contact_service.get_contacts_for_client(page)


@ContactsRouter.get(
    "/pid",
    response_model=ContactOutputDto,
    summary="search user by pid only for active account",
    description="This will display info only for active account"
)
def get_contact_by_pid_for_client(
        pid: str,
        contact_service: ContactsService = Depends()
):
    return contact_service.get_contact_by_pid_for_client(pid)


@ContactsRouter.get(
    "/number",
    response_model=ContactOutputDto,
    summary="search user by contact unique number(uid) including delete or active",
    description="search user by contact unique number(uid) including delete or active"
)
def get_contact_by_uid_for_client(
        number: str,
        contact_service: ContactsService = Depends()
):
    return contact_service.get_contact_by_uid_for_client(number)


@ContactsRouter.get(
    "/id",
    response_model=ContactOutputDto | None,
    summary="search user by his id in db only for active account",
    description="search user by his id in db only for active account"
)
def get_contact_by_id_for_client(
        id: int,
        contact_service: ContactsService = Depends()
):
    return contact_service.get_contact_by_id_for_client(id)


@ContactsRouter.get(
    "/type",
    response_model=List[ContactOutputDto],
    summary="search user by contact type only for active account",
    description="search user by contact type only for active account"
)
def get_contact_by_type_for_client(
        contact_type: str,
        offset: int, limit: int,
        contact_service: ContactsService = Depends()
):
    return contact_service.get_contact_by_type_for_client(contact_type, offset, limit)
