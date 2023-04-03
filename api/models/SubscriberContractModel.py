from datetime import datetime, date
from typing import List

from sqlalchemy import JSON, ForeignKey, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.BaseModel import EntityMeta


class SubscriberContract(EntityMeta):
    __tablename__ = "subscriber_contract"

    id: Mapped[int] = mapped_column(primary_key=True)
    infos: Mapped[JSON] = mapped_column(JSON)
    customer_id: Mapped[int] = mapped_column(ForeignKey('contacts.id'))
    contacts: Mapped[List["Contacts"]] = relationship(
        back_populates="subscriber_contract"
    )

    opening_date: Mapped[datetime]
    closing_date: Mapped[datetime]

    power_of_energy: Mapped[int]
    creation_at: Mapped[date]
    update_at: Mapped[date]
    delete_at: Mapped[date]


