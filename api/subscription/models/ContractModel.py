from typing import List
from datetime import datetime
from api.configs.BaseModel import EntityMeta
from sqlalchemy.dialects.mysql import BIGINT, MEDIUMINT
from sqlalchemy import JSON, ForeignKey, Column, Boolean, DateTime
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)


class Contract(EntityMeta):
    __tablename__ = "contracts"

    """
    id: Mapped[int] = mapped_column(MEDIUMINT(unsigned=True), index=True, primary_key=True)
    contract_number: Mapped[int] = mapped_column(BIGINT(unsigned=True), index=True, unique=True, nullable=False)
    customer_number: Mapped[str] = mapped_column(BIGINT(unsigned=True), index=True, nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("contacts.id"))
    infos: Mapped[JSON] = mapped_column(JSON)
    attachment: Mapped[dict] = mapped_column(JSON, default=None, nullable=True)
    is_activated: Mapped[bool] = mapped_column(default=False)

    opening_date: Mapped[datetime] = mapped_column(nullable=True, default=None)
    closing_date: Mapped[datetime] = mapped_column(nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=True, default=None)
    deleted_at: Mapped[datetime] = mapped_column(nullable=True, default=None)

    contacts: Mapped[List["Contact"]] = relationship(back_populates="contracts")
    """
    
    id = Column(MEDIUMINT(unsigned=True), primary_key=True, index=True)
    contract_number = Column(BIGINT(unsigned=True), index=True, unique=True, nullable=False)
    customer_number = Column(BIGINT(unsigned=True), index=True, nullable=False)
    customer_id = Column(MEDIUMINT(unsigned=True), ForeignKey("contacts.id"), nullable=False)
    infos = Column(JSON, nullable=False)
    attachment = Column(JSON, nullable=False)
    is_activated = Column(Boolean, index=True, default=True)
    opening_date = Column(DateTime(timezone=True), nullable=False)
    closing_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow().isoformat(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow().isoformat(), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    contact = relationship("Contact", back_populates="contracts")
    
    def normalize(self):
        return {
            "id": self.id,
            "infos": self.infos,
            "customer_id": self.customer_id,
            "created_at": self.created_at,
            "deleted_at": self.deleted_at,
            "updated_at": self.updated_at,
            "opening_date": self.opening_date,
            "closing_date": self.closing_date,
        }
