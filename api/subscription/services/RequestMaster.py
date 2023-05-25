from typing import List

import requests
from fastapi import HTTPException, status
from fastapi.openapi.models import Response
from fastapi.encoders import jsonable_encoder

from api.subscription.exceptions import BillingRequestException, RequestResourceError
from api.subscription.schemas.SubscriberContractSchema import InvoiceDetails, Invoice, \
    ContractInvoiceForBillingService, PricingDto


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
    def get_pricing_info(cls, subscriber_code: int, url: str, token: str) -> PricingDto:
        header = {
            "Authorization": token
        }
        try:
            response = requests.get(url, params=subscriber_code)
            if response.status_code == 200:
                response.text: PricingDto = jsonable_encoder(response.text)
                return [PricingDto(

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
