from typing import List

from fastapi import Depends

from api.models.LogsModel import Logs
from api.repositories.LogsRepository import LogsRepository
from api.schemas.pydantic.LogsSchema import LogsSchema


class LogsService:
    logsRepository: LogsRepository

    def __init__(self, logsRepository: LogsRepository = Depends()):
        self.logsRepository = logsRepository

    def createLogs(self,  logsSchema: LogsSchema):
        return self.logsRepository.createLogs(
            Logs(
               infos=logsSchema
            )
        )

    def getLogsByUserIdAndEntityName(self, userId: int, entityName: str, start: int, limit: int) -> List[Logs]:
        return self.logsRepository.getLogsByUserIdAndEntityName(userId, entityName, start, limit)

    def getLogsByItemIdAndEntityName(self, itemId: int, entityName: str, start: int, limit: int) -> List[Logs]:
        return self.logsRepository.getLogsByItemIdAndEntityName(itemId, entityName, start, limit)

    def getLogsByUserIdItemIdAndEntityName(self, userId: int, entityName: str, itemId: int, start: int, limit: int) -> List[Logs]:
        return self.logsRepository.getLogsByUserIdItemIdAndEntityName(userId, entityName, itemId, start, limit)

    def getLogsByItemId(self, itemId: int, start: int, limit: int) -> List[Logs]:
        return self.logsRepository.getLogsByItemId(itemId, start, limit)

    def getLogsByUserId(self, userId: int, start: int, limit: int) -> List[Logs]:
        return self.logsRepository.getLogsByUserId(userId, start, limit)

    def getLogsByEntityName(self, entityName: str, start: int, limit: int) -> List[Logs]:
        return self.getLogsByEntityName(entityName, start, limit)




