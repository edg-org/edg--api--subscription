from typing import Dict
from datetime import date, datetime, time
from sqlalchemy.dialects.mysql import JSON
from api.configs.BaseModel import EntityMeta
from api.subscription.models.ContractModel import Contract
from sqlalchemy import (
    String,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

class Contacts(EntityMeta):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    infos: Mapped[Dict] = mapped_column(JSON)
    is_activated: Mapped[bool] = mapped_column(default=True)
    customer_number: Mapped[str] = mapped_column(String(10), index=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(default=None, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(default=None, nullable=True)
    contracts: Mapped["contacts"] = relationship("Contract", back_populates="contacts")

    def normalize(self):
        return {
            "id": self.id.__str__(),
            "infos": self.infos,
            "creation_at": self.created_at.__str__(),
            "update_at": self.updated_at.__str__(),
            "delete_at": self.deleted_at.__str__(),
            "contact_uid": self.customer_number.__str__(),
        }