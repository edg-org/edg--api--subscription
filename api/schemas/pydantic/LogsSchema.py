from pydantic import BaseModel


class LogsInfo(BaseModel):
    entity_name: str
    item_id: int
    user_id: int
    action: str
    previous_data: dict


class LogsSchema(BaseModel):
    infos: LogsInfo

