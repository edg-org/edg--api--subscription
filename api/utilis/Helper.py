from typing import List
from httpx import AsyncClient
from fastapi import HTTPException
from fastapi.openapi.models import Response
from fastapi.encoders import jsonable_encoder

from api.subscription.exceptions import (
    BillingRequestException, 
    RequestResourceError
)
from api.subscription.schemas.ContractSchema import (
    PricingDto,
    InvoiceDetails, 
    ContractInvoiceForBillingService
)

class Helper:
    @classmethod
    def contactNumber(cls, identityNumber: str) -> str:
        return "CL"+str(abs(hash(identityNumber)) % (10**7))
    
    @classmethod
    async def generic_request_query(cls, url: str, token: str) -> Response:
        header = {"Authorization": token}
        client = AsyncClient()
        response = await client.get(url, headers=header)
        status_code=response.status_code 
        
        if status_code != 200:
            if status_code == 401:
                detail=f"{response.text} : Please you have to authenticate, login please"
            elif status_code == 403:
                detail=f"{response.text} : The access to this resource is forbidden"
            else:
                detail=response.text                
            
            raise HTTPException(
                    status_code=status_code,
                    detail=detail
                )
        return response.text

    @classmethod
    async def get_pricing_info(cls, subscriber_code: int, url: str, token: str) -> PricingDto:
        header = {"Authorization": token}
        try:
            client = AsyncClient()
            response = await client.get(url, params=subscriber_code)
            if response.status_code == 200:
                response.text: PricingDto = jsonable_encoder(response.text)
                return [PricingDto(

                ) for billing in response.text]
            raise BillingRequestException
        except:
            raise RequestResourceError

    @classmethod
    async def get_invoice(cls, contractParam: ContractInvoiceForBillingService, url: str, token: str) -> List[InvoiceDetails]:
        header = {"Authorization": token}
        try:
            client = AsyncClient()
            response = await client.get(url, params=contractParam)
            if response.status_code == 200:
                response.text: List[InvoiceDetails] = jsonable_encoder(response.text)
                return [InvoiceDetails(
                    contract_number=invoiceDetails.contract_number,
                    invoice=invoiceDetails.invoice
                ) for invoiceDetails in response.text]
        except:
            raise RequestResourceError