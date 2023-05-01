from datetime import date
from typing import Dict

# from MySQLdb.times import Date
from sqlalchemy import (
    String,
)
from sqlalchemy.dialects.mysql import JSON

from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.BaseModel import EntityMeta
from api.models.SubscriberContractModel import SubscriberContract


class Contacts(EntityMeta):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    infos: Mapped[Dict] = mapped_column(JSON)
    is_activated: Mapped[bool] = mapped_column(default=True)
    contact_uid: Mapped[str] = mapped_column(String(10))
    created_at: Mapped[date] = mapped_column(default=date.today())
    updated_at: Mapped[date] = mapped_column(default=None, nullable=True)
    deleted_at: Mapped[date] = mapped_column(default=None, nullable=True)

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
            "contact_uid": self.contact_uid.__str__()
        }



