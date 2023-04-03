from typing import List

from fastapi import APIRouter, Depends

from api.models.ContactsModel import Contacts
from api.schemas.pydantic.ContactsSchema import ContactsSchema
from api.services.ContactsService import ContactsService

ContactsRouter = APIRouter(
    prefix="/v1/contacts", tags=["contacts"]
)


@ContactsRouter.post(
    "/",
    summary="create user",
    description="use this endpoint to create a new user"
)
def create_contact(
        contact: ContactsSchema,
        contact_service: ContactsService = Depends()
):
    return contact_service.create_contact(contact).normalize()


@ContactsRouter.put(
    "/{pid}",
    summary="update user by pid",
    description="use this endpoint to update user infos"
)
def update_contact(
        pid: str,
        contact: ContactsSchema,
        contact_service: ContactsService = Depends()
):
    return contact_service.update_contact(pid, contact).normalize()


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
    summary="search user by phone only for active account",
    description="This will display info only for active account"
)
def get_contact_by_phone_for_client(
        phone: str,
        contact_service: ContactsService = Depends()):
    return contact_service.get_contact_by_phone_for_client(phone)


@ContactsRouter.get(
    "/email",
    summary="search user by email only for active account",
    description="This will display info only for active account"
)
def get_contact_by_email_for_client(
        email: str,
        contact_service: ContactsService = Depends()):
    return contact_service.get_contact_by_email_for_client(email)


@ContactsRouter.get(
    "",
    summary="search users for active account",
    description="This will display info only for active account"
)
def get_contacts_for_client(
        offset: int,
        limit: int,
        contact_service: ContactsService = Depends()
):
    return contact_service.get_contacts_for_client(offset, limit)


@ContactsRouter.get(
    "/pid",
    summary="search user by pid only for active account",
    description="This will display info only for active account"
)
def get_contact_by_pid_for_client(
        pid: str,
        contact_service: ContactsService = Depends()
):
    return contact_service.get_contact_by_pid_for_client(pid).normalize()


@ContactsRouter.get(
    "/contact-uid",
    summary="search user by contact unique number(uid) including delete or active",
    description="search user by contact unique number(uid) including delete or active"
)
def get_contact_by_uid_for_client(
        contact_uid: str,
        contact_service: ContactsService = Depends()
):
    return contact_service.get_contact_by_uid_for_client(contact_uid).normalize()


@ContactsRouter.get(
    "/id",
    summary="search user by his id in db only for active account",
    description="search user by his id in db only for active account"
)
def get_contact_by_id_for_client(
        id: int,
        contact_service: ContactsService = Depends()
):
    return contact_service.get_contact_by_id_for_client(id)


@ContactsRouter.get(
    "/contact-type",
    summary="search user by contact type only for active account",
    description="search user by contact type only for active account"
)
def get_contact_by_type_for_client(
        contact_type: str,
        offset: int, limit: int,
        contact_service: ContactsService = Depends()
):
    return contact_service.get_contact_by_type_for_client(contact_type, offset, limit)
