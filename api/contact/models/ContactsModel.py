from datetime import date, datetime, time
from typing import Dict

# from MySQLdb.times import Date
from sqlalchemy import (
    String, func,
)
from sqlalchemy.dialects.mysql import JSON

from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.contact.models.BaseModel import EntityMeta
from api.contact.models.SubscriberContractModel import SubscriberContract


class Contacts(EntityMeta):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    infos: Mapped[Dict] = mapped_column(JSON)
    is_activated: Mapped[bool] = mapped_column(default=True)
    customer_number: Mapped[str] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(default=None, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(default=None, nullable=True)

    subscriber_contract: Mapped[SubscriberContract] = relationship(
        "SubscriberContract", back_populates="contacts"
    )

    def normalize(self):
        return {
            "id": self.id.__str__(),
            "infos": self.infos,
            "creation_at": self.created_at.__str__(),
            "update_at": self.updated_at.__str__(),
            "delete_at": self.deleted_at.__str__(),
            "contact_uid": self.customer_number.__str__()
        }



