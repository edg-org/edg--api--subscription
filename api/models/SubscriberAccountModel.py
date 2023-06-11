import decimal
from datetime import datetime, date
from typing import List

from sqlalchemy import DATETIME, DECIMAL, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.BaseModel import EntityMeta


class SubscriberAccount(EntityMeta):
    __tablename__ = "subscriber_account"

    costumer_id: Mapped[int] = mapped_column(ForeignKey('contacts.id'))

    contacts: Mapped[List["Contacts"]] = relationship(
        back_populates="subscriber_account"
    )
    account_balance_date: Mapped[datetime] = mapped_column(primary_key=True, autoincrement=False)
    total_amount_due: Mapped[int]
    total_amount_paid: Mapped[int]
    account_balance: Mapped[int]
    creation_at: Mapped[date]
    update_at: Mapped[date]
    delete_at: Mapped[date]
