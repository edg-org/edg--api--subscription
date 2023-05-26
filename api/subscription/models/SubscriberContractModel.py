from datetime import date, datetime
from typing import List

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.contact.models.BaseModel import EntityMeta


class SubscriberContract(EntityMeta):
    __tablename__ = "subscriber_contract"

    id: Mapped[int] = mapped_column(primary_key=True)
    infos: Mapped[JSON] = mapped_column(JSON)
    customer_id: Mapped[int] = mapped_column(ForeignKey('contacts.id'))
    customer_number: Mapped[str] = mapped_column(nullable=False)
    contacts: Mapped[List["Contacts"]] = relationship(
        "Contacts", back_populates="subscriber_contract"
    )

    opening_date: Mapped[datetime] = mapped_column(nullable=True, default=None)
    closing_date: Mapped[datetime] = mapped_column(nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=True, default=None)
    deleted_at: Mapped[datetime] = mapped_column(nullable=True, default=None)
    is_activated: Mapped[bool] = mapped_column(default=False)
    contract_number: Mapped[str] = mapped_column(String(10))
    attachment: Mapped[dict] = mapped_column(JSON, default=None, nullable=True)

    def normalize(self):
        return {
            "id": self.id,
            "infos": self.infos,
            "customer_id": self.customer_id,
            "created_at": self.created_at,
            "deleted_at": self.deleted_at,
            "updated_at": self.updated_at,
            "opening_date": self.opening_date,
            "closing_date": self.closing_date

        }
