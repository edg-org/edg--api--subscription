import requests
from fastapi import HTTPException, status
from fastapi.openapi.models import Response
from fastapi.encoders import jsonable_encoder

from api.subscription.exceptions import BillingRequestException
from api.subscription.schemas.SubscriberContractSchema import BillingDto


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


    @classmethod
    def get_billing_info(cls, subscriber_code: int, url: str, token: str) -> BillingDto:
        header = {
            "Authorization": token
        }
        response = requests.get(url+"/"+str(subscriber_code))
        if response.status_code == 200:
            response = jsonable_encoder(response.text)
            return BillingDto(
                subscription_type=response.subscription_type,
                payment_deadline=response.payment_deadline,
                deadline_unit_time=response.deadline_unit_time,
                prime=response.prime,
                pricing=response.pricing,
                dunning=response.dunning,
            )
        raise BillingRequestException
