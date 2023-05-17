from typing import List

import requests
from fastapi import HTTPException, status
from fastapi.openapi.models import Response
from fastapi.encoders import jsonable_encoder

from api.subscription.exceptions import BillingRequestException, RequestResourceError
from api.subscription.schemas.SubscriberContractSchema import BillingDto, InvoiceDetails, Invoice, \
    ContractInvoiceForBillingService


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
    def get_billing_info(cls, subscriber_code: List[str], url: str, token: str) -> List[BillingDto]:
        header = {
            "Authorization": token
        }
        try:
            response = requests.get(url, params=subscriber_code)
            if response.status_code == 200:
                response.text: List[BillingDto] = jsonable_encoder(response.text)
                return [BillingDto(
                    subscription_type=billing.subscription_type,
                    payment_deadline=billing.payment_deadline,
                    deadline_unit_time=billing.deadline_unit_time,
                    prime=billing.prime,
                    pricing=billing.pricing,
                    dunning=billing.dunning,
                ) for billing in response.text]
            raise BillingRequestException
        except:
            raise RequestResourceError

    @classmethod
    def get_invoice(cls, contractParam: ContractInvoiceForBillingService, url: str, token: str) -> List[InvoiceDetails]:
        header = {
            "Authorization": token
        }
        try:
            response = requests.get(url, params=contractParam)
            if response.status_code == 200:
                response.text: List[InvoiceDetails] = jsonable_encoder(response.text)
                return [InvoiceDetails(
                    contract_number=invoiceDetails.contract_number,
                    invoice=invoiceDetails.invoice
                ) for invoiceDetails in response.text]
        except:
            raise RequestResourceError
