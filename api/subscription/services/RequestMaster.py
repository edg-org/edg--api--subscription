import json
from typing import List, Any
from httpx import AsyncClient
import requests
from fastapi import HTTPException, status
from fastapi.openapi.models import Response
from fastapi.encoders import jsonable_encoder

from api.subscription.exceptions import BillingRequestException, RequestResourceError
from api.subscription.schemas.ContractSchema import InvoiceDetails, Invoice, \
    ContractInvoiceForBillingService, PricingDto


class RequestMaster:

    @classmethod
    async def generic_request_query(cls, url: str, token: str) -> Response:
        header = {
            "Authorization": token
        }
        client = AsyncClient()

        response = await client.get(url, headers=header)
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
    async def get_pricing_info(cls, url: str, token: str) -> Any:
        header = {
            "Authorization": "Bearer "+token
        }
        try:
            client = AsyncClient()
            response = await client.get(url, headers=header)
            print("===============>Response =======================>", response.status_code)

            if response.status_code == 200:
                return response.text
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

