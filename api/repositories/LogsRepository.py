from typing import List

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models.LogsModel import Logs
from api.schemas.pydantic.LogsSchema import LogsSchema


class LogsRepository:
    db: Session

    def __init__(self, db: Session = Depends()):
        self.db = db

    def createLogs(self, logs: Logs) -> Logs:
        self.db.add(logs)
        self.db.commit()
        self.db.refresh(logs)
        return logs

    def getLogsByItemIdAndEntityName(self, itemId: int, entityName: str, start: int, limit: int) -> List[Logs]:
        return select(Logs).where(
            Logs.infos['item_id'] == itemId,
            Logs.infos['entity_name'] == entityName
        ).offset(start).limit(limit).all()

    def getLogsByUserIdAndEntityName(self, userId: int, entityName: str, start: int, limit: int) -> List[Logs]:
        return select(Logs).where(
            Logs.infos['user_id'] == userId,
            Logs.infos['entity_name'] == entityName
        ).offset(start).limit(limit).all()

    def getLogsByUserIdItemIdAndEntityName(self, userId: int, entityName: str, itemId: int, start: int, limit: int) -> List[Logs]:
        return select(Logs).filter(
            Logs.infos['item_id'] == itemId,
            Logs.infos['user_id'] == userId,
            Logs.infos['entity_name'] == entityName
        ).offset(start).limit(limit).all()

    def getLogsByItemId(self, itemId: int, start: int, limit: int) -> List[Logs]:
        return select(Logs).where(
            Logs.infos['item_id'] == itemId
        ).offset(start).limit(limit).all()

    def getLogsByUserId(self, userId: int, start: int, limit: int) -> List[Logs]:
        return select(Logs).where(
            Logs.infos['user_id'] == userId
        ).offset(start).limit(limit).all()

    def getLogsByEntityName(self, entityName: str, start: int, limit: int) -> List[Logs]:
        return select(Logs).where(
            Logs.infos['entity_name'] == entityName
        ).offset(start).limit(limit).all()
