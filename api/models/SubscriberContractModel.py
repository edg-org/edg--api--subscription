from datetime import datetime, date
from typing import List

from sqlalchemy import JSON, ForeignKey, DECIMAL, String
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

    opening_date: Mapped[date] = mapped_column(nullable=True)
    closing_date: Mapped[date] = mapped_column(nullable=True)
    power_of_energy: Mapped[str] = mapped_column(String(45))
    created_at: Mapped[date] = mapped_column(default=date.today())
    updated_at: Mapped[date] = mapped_column(nullable=True)
    deleted_at: Mapped[date] = mapped_column(nullable=True)
    is_activated: Mapped[bool] = mapped_column(default=False)
    contract_uid: Mapped[str] = mapped_column(String(10))

    def normalize(self):
        return {
            "id": self.id,
            "infos": self.infos,
            "customer_id": self.customer_id,
            "power_of_energy": self.power_of_energy,
            "created_at": self.created_at,
            "deleted_at": self.deleted_at,
            "updated_at": self.updated_at,
            "opening_date": self.opening_date,
            "closing_date": self.closing_date

        }