from typing import List

from fastapi import APIRouter, Depends

from api.models.ContactsModel import Contacts
from api.schemas.pydantic.ContactsSchema import ContactOutputDto
from api.services.ContactsService import ContactsService

InvestigateContactRouter = APIRouter(
    prefix="/v1/investigate/contacts", tags=["Contacts investigation"]
)


@InvestigateContactRouter.get(
    "/pid",
    response_model=ContactOutputDto,
    summary="search user by pid including delete or active",
    description="search user by pid including delete or active"
)
def get_contact_by_pid(
        pid: str,
        contact_service: ContactsService = Depends()
):
    return contact_service.get_contact_by_pid_for_admin(pid)


@InvestigateContactRouter.get(
    "",
    response_model=List[ContactOutputDto],
    summary="fetch all contact including deleted end active ",
    description="fetch all contact including deleted end active"
)
def get_contacts(
        offset: int,
        limit: int,
        contact_service: ContactsService = Depends()
):
    return contact_service.get_contacts_for_admin(offset, limit)


@InvestigateContactRouter.get(
    "/email",
    response_model=ContactOutputDto,
    summary="search user by email including delete or active",
    description="search user email pid including delete or active"
)
def get_contact_by_email(
        email: str,
        contact_service: ContactsService = Depends()):
    return contact_service.get_contact_by_email_for_admin(email)


@InvestigateContactRouter.get(
    "/phone",
    response_model=ContactOutputDto,
    summary="search user by phone number including delete or active",
    description="search user by phone number including delete or active"
)
def get_contact_by_phone(
        phone: str,
        contact_service: ContactsService = Depends()):
    return contact_service.get_contact_by_phone_for_admin(phone)


@InvestigateContactRouter.get(
    "/contact-uid",
    response_model=ContactOutputDto,
    summary="search user by contact unique number(uid) including delete or active",
    description="search user by contact unique number(uid) including delete or active"
)
def get_contact_by_uid_for_admin(
        contact_uid: str,
        contact_service: ContactsService = Depends()
):
    return contact_service.get_contact_by_uid_for_admin(contact_uid)


@InvestigateContactRouter.get(
    "/id",
    response_model=ContactOutputDto,
    summary="search user by his id in db including delete or active",
    description="search user by his id in db including delete or active"
)
def get_contact_by_id_for_admin(
        id: int,
        contact_service: ContactsService = Depends()
):
    return contact_service.get_contact_by_id_for_admin(id)


@InvestigateContactRouter.get(
    "/contact-type",
    response_model=List[ContactOutputDto],
    summary="search user by contact type only for active account",
    description="search user by contact type only for active account"
)
def get_contact_by_type_for_admin(
        contact_type: str,
        offset: int, limit: int,
        contact_service: ContactsService = Depends()
):
    return contact_service.get_contact_by_type_for_admin(contact_type, offset, limit)
