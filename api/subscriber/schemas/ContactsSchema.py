import json
import logging
from typing import List, Optional
from datetime import datetime, date
from api.constant import OpenAPIFieldDescription
from api.configs.SchemaBase import (
    AllOptional,
    HideFields,
)
from pydantic import (
    BaseModel,
    validator,
    EmailStr,
    constr,
    Field,
)

class Identity(BaseModel):
    type: str
    pid: str
    given_date: date
    expire_date: date

    @validator("given_date", allow_reuse=True)
    def givenDateInFuture(cls, value):
        if value > date.today():
            raise ValueError(
                "The delivery date of your ID cannot be higher than the current one"
            )
        return value

    @validator("expire_date", allow_reuse=True)
    def expireDateInPas(cls, ex_date):
        if ex_date < date.today():
            raise ValueError("Your ID has expired")
        return ex_date


class Address(BaseModel):
    quartier: str
    city: str
    email: EmailStr
    telephone: constr(regex=r"^\+224-\d{3}-\d{2}-\d{2}-\d{2}$")


class ContactInfos(HideFields):
    type: str
    lastname: str
    firstname: str
    birthday: date
    job: str
    identity: Identity
    address: Address

    @validator("birthday")
    def check_age(cls, value):
        if cls.__name__ != "ContactsInputUpdateDto":
            today = date.today()
            age = (
                today.year
                - value.year
                - (
                    (today.month, today.day)
                    < (value.month, value.day)
                )
            )
            if age < 18:
                raise ValueError("You should be over the age of 18")
            return value

    @validator("type", allow_reuse=True)
    def validateType(cls, type_value: str):
        if type_value.lower().capitalize() in [
            "Client",
            "Prospect",
            "Abonné",
        ]:
            return type_value
        raise ValueError(
            "Invalid contact type, the contact type should by one "
            "of the following (Client, Abonné or Prospect)"
        )


class IdentityOutput(Identity, metaclass=AllOptional):
    pass

class ContactInfosOutput(ContactInfos, metaclass=AllOptional):
    pass

class ContactsInputDto(ContactInfos):
    pass

class ContactsInputUpdateDto(ContactInfos):
    class Config:
        hide_fields = {"birthday"}

class ContactOutputDto(BaseModel):
    id: int | None
    infos: ContactInfosOutput | None
    is_activated: bool | None
    customer_number: str | None
    created_at: datetime | None
    updated_at: datetime | None
    deleted_at: datetime | None

class ContactDtoWithPagination(BaseModel):
    count: int
    total: int
    offset: int
    limit: int
    data: List[ContactOutputDto] | None

class SearchByParams(BaseModel):
    pid: str | None = Field(description=OpenAPIFieldDescription.PID)
    phone: str | None = Field(description=OpenAPIFieldDescription.PHONE)
    email: str | None = Field(description=OpenAPIFieldDescription.EMAIL)
    customer_number: str | None = Field(description=OpenAPIFieldDescription.CUSTOMER_NUMBER)
    status: bool | None = Field(description=OpenAPIFieldDescription.PID)

class SearchAllContact(BaseModel):
    type: str | None = Field(description=OpenAPIFieldDescription.CONTACT_TYPE)
    status: bool | None = Field(description=OpenAPIFieldDescription.PID)