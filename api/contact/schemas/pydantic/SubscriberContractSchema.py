import decimal
from datetime import datetime
from typing import Dict

from pydantic import BaseModel

from api.contact.models.ContactsModel import Contacts


class SubscriberContractSchema(BaseModel):
    infos: Dict
    customer_id: int
    opening_date: datetime
    closing_date: datetime
    power_of_energy: decimal


class SubscriberContractRead(BaseModel):
    infos: Dict
    contacts: Contacts
    opening_date: datetime
    closing_date: datetime
    power_of_energy: decimal
