from datetime import datetime
from typing import Any

from fastapi import Depends
from sqlalchemy import select, Select
from sqlalchemy.orm import Session

from api.configs.Database import get_db_connection
from api.schemas.pydantic.SubscriberAccountSchema import SubscriberAccountSchema, SubscriberAccountRead
from api.models.SubscriberAccountModel import SubscriberAccount


class SubscriberAccountRepository:
    db: Session

    def __init__(self, db: Session = Depends(get_db_connection)):
        self.db = db

    def createSubscriberAccount(self, subscriberAccount: SubscriberAccount) -> SubscriberAccountRead:
        self.db.add(subscriberAccount)
        self.db.commit()
        self.db.refresh()
        return SubscriberAccountRead(
            costumerId=subscriberAccount.costumerId,
            accountBalanceDate=subscriberAccount.account_balance_date,
            totalAmountDue=subscriberAccount.total_amount_due,
            totalAmountPaid=subscriberAccount.total_amount_paid,
            accountBalance=subscriberAccount.account_balance
        )

    def updateSubscriberAccount(self,
                                costumer_id: int,
                                account_balance_date: datetime,
                                subscriberAccount: SubscriberAccount) -> SubscriberAccountRead:
        query: SubscriberAccount = self.getSubscriberAccount(costumer_id,
                                                             account_balance_date)  # check if contact has subscribed to account
        if self.db.execute(query) is None:
            raise  Exception("Vous ne pouvez pas modifier une instance qui n'existe pas")
        subscriberAccount.costumerId = costumer_id
        subscriberAccount.account_balance_date = account_balance_date
        self.db.merge(subscriberAccount)
        self.db.commit()
        return SubscriberAccountRead(
            contacts=subscriberAccount.contacts,
            accountBalanceDate=subscriberAccount.account_balance_date,
            totalAmountDue=subscriberAccount.total_amount_due,
            totalAmountPaid=subscriberAccount.total_amount_paid,
            accountBalance=subscriberAccount.account_balance

        )

    def getSubscriberAccount(self,
                             costumer_id: int,
                             account_balance_date: datetime
                             ) -> SubscriberAccountRead:
        query: SubscriberAccount = select(SubscriberAccount).where(costumer_id == SubscriberAccount.costumerId,
                                                                   account_balance_date.__eq__(
                                                                       SubscriberAccount.accountBalance))

        return SubscriberAccountRead(
            contacts=query.contacts,
            accountBalanceDate=query.account_balance_date,
            totalAmountDue=query.total_amount_due,
            totalAmountPaid=query.total_amount_paid,
            accountBalance=query.account_balance
        )

    def deleteAccount(self, costumer_id: int,
                      account_balance_date: datetime) -> None:
        query = self.getSubscriberAccount(costumer_id, account_balance_date)

        if self.db.execute(query).first() is not None:
            self.db.delete(query)
            self.db.flush()
        else:
            raise Exception("Vous ne pouvez pas supprimer une instance qui n'existe pas ")


