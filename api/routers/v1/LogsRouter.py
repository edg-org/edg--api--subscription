from fastapi import APIRouter, Depends


LogsRouter = APIRouter(
    prefix="/v1/logs", tags=["Logs"]
)


