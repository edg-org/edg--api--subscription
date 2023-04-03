from typing import Dict


from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from api.models.BaseModel import EntityMeta


class Logs(EntityMeta):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    infos: Mapped[Dict] = mapped_column(JSON)

    def normalize(self):
        return {
            "id": self.id.__str__(),
            "infos": self.infos.__str__()
        }
