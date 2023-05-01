import decimal
from datetime import datetime
from typing import List, Dict

from pydantic import BaseModel

from api.models.ContactsModel import Contacts


class SubscriberAccount(BaseModel):
    account_balance_date: datetime
    total_amount_due: decimal
    total_amount_paid: datetime
    account_balance: decimal


class SubscriberAccountSchema(SubscriberAccount):
    costumer_id: int


class SubscriberAccountRead(SubscriberAccount):
    contacts: List[Contacts]

    def normalize(self):
        return {
            "costumerId": self.costumerId,
            "contacts": self.contacts,
            "account_balance_date": self.account_balance_date,
            "total_amount_due": self.total_amount_due,
            "total_amount_paid": self.total_amount_paid,
            "account_balance": self.account_balance
        }
