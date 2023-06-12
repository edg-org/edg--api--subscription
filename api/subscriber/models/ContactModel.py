from datetime import datetime
from sqlalchemy.orm import relationship
from api.configs.BaseModel import EntityMeta
from sqlalchemy import JSON, Boolean, DateTime, Column
from sqlalchemy.dialects.mysql import BIGINT, MEDIUMINT

class Contact(EntityMeta):
    
    __tablename__ = "contacts"
    
    id = Column(MEDIUMINT(unsigned=True), primary_key=True, index=True)
    customer_number = Column(BIGINT(unsigned=True), index=True, unique=True, nullable=False)
    infos = Column(JSON, nullable=False)
    is_activated = Column(Boolean, index=True, default=True)
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow().isoformat(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow().isoformat(), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    contracts = relationship("Contract", back_populates="contact")

    def normalize(self):
        return {
            "id": self.id.__str__(),
            "infos": self.infos,
            "creation_at": self.created_at.__str__(),
            "update_at": self.updated_at.__str__(),
            "delete_at": self.deleted_at.__str__(),
            "contact_uid": self.customer_number.__str__(),
        }