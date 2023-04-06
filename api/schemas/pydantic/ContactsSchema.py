import json
import logging
from datetime import datetime, date


from pydantic import BaseModel, validator, EmailStr, constr


class Identity(BaseModel):
    type: str
    pid: str
    given_date: date
    expire_date: date

    @validator('given_date', allow_reuse=True)
    def givenDateInFuture(cls, value):
        if value > date.today():
            raise ValueError("The delivery date of your ID cannot be higher than the current one")
        return value

    @validator('expire_date', allow_reuse=True)
    def expireDateInPas(cls, ex_date):
        if ex_date < date.today():
            raise ValueError("Your ID has expired")
        return ex_date


class Address(BaseModel):
    quartier: str
    email: EmailStr
    telephone: constr(regex=r'^\+224-\d{3}-\d{2}-\d{2}-\d{2}$')


class ContactInfos(BaseModel):
    type: str
    name: str
    firstname: str
    birthday: date
    job: str
    identity: Identity
    address: Address

    @validator('birthday')
    def check_age(cls, value):
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 18:
            raise ValueError("You should be over the age of 18")
        return value

    @validator('type', allow_reuse=True)
    def validateType(cls, type_value: str):
        if type_value.lower().capitalize() in ['Client', 'Prospect', 'Abonné']:
            return type_value
        raise ValueError("Invalid contact type, the contact type should by one "
                             "of the following (Client, Abonné or Prospect)")


class ContactsSchema(BaseModel):
    infos: ContactInfos