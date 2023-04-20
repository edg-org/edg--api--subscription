import logging
from http import client
from numbers import Number
from typing import Any
from wsgiref import headers

import requests
from fastapi import HTTPException, status
from fastapi.openapi.models import Response

from subscriber_api.schemas.ParseScope import ParseScope


class RequestMaster:

    @classmethod
    async def generic_request_query(cls, url: str, token: str) -> Response:
        header = {
            "Authorization": token
        }
        response = requests.get(url, headers=header)
        # logging.warning("response status code ", response.status_code)
        if response.status_code == 403:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The access to this resource is forbidden",
            )
        if response.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Please you have to authenticate, login please"
            )
        return response.text
