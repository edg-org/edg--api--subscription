from enum import Enum
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass
from api.subscriber.schemas.ContactsSchema import ContactInfosOutput
from api.configs.SchemaBase import (
    HideFields,
    AllOptional,
)
from api.subscription.constant import OpenAPIFieldDescription

class SubscriptionLevel(BaseModel):
    name: str = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_LEVEL_NAME)
    payment_mode: List[str] = Field(description=OpenAPIFieldDescription.PAYMENT_MODE_NAME)

class Agency(BaseModel):
    name: str = Field(description=OpenAPIFieldDescription.AGENCY_NAME)
    code: str = Field(description=OpenAPIFieldDescription.AGENCY_CODE)
    tel: str = Field(description=OpenAPIFieldDescription.AGENCY_TEL)
    email: str = Field(description=OpenAPIFieldDescription.AGENCY_EMAIL)

class SubscriptionType(BaseModel):
    code: int = Field(description=OpenAPIFieldDescription.SUBSCRIPTION_CODE)
    name: str = Field(description=OpenAPIFieldDescription.SUBSCRIPTION_NAME)

class ConsumptionEstimated(BaseModel):
    value: int = Field(description=OpenAPIFieldDescription.SUBSCRIPTION_CODE)
    measurement_unit: str = Field(description=OpenAPIFieldDescription.SUBSCRIPTION_NAME)

class DeliveryPoint(HideFields):
    number: str = Field(description=OpenAPIFieldDescription.DELIVERY_NUMBER)
    metric_number: Optional[str] = Field(description=OpenAPIFieldDescription.METRIC_NUMBER)

class DeliveryPointUpdate(DeliveryPoint):
    class Config:
        hide_fields = {"number"}

class Equipment(BaseModel):
    total: int = Field(description=OpenAPIFieldDescription.AMOUNT_EQUIPMENT)
    details: List[str] = Field(description=OpenAPIFieldDescription.EQUIPMENT_LIST)

class HomeInfos(BaseModel):
    surface: int = Field(description=OpenAPIFieldDescription.SURFACE)
    occupier_number: int = Field(description=OpenAPIFieldDescription.OCCUPIER_NUMBER)
    equipment: Equipment = Field(description=OpenAPIFieldDescription.EQUIPMENT)

class Slices(BaseModel):
    slice_name: str
    lower_index: int
    upper_index: int
    unit_price: int

class Pricing(BaseModel):
    name: str = Field(description=OpenAPIFieldDescription.SLICE_NAME)
    subscription_fee: int = Field(description=OpenAPIFieldDescription.LOWER_INDEX)
    slices: List[Slices] = Field(description=OpenAPIFieldDescription.UPPER_INDEX)

class Dunning(BaseModel):
    name: str = Field(description=OpenAPIFieldDescription.DUNNING_NAME)
    rank: int = Field(description=OpenAPIFieldDescription.DUNNING_RANK)
    payment_deadline: int = Field(description=OpenAPIFieldDescription.PAYMENT_DEADLINE)
    delay_penality_rate: int = Field(description=OpenAPIFieldDescription.DELAY_PENALTY_RATE)

class ContractInfo(HideFields):
    consumption_estimated: ConsumptionEstimated
    subscription_type: SubscriptionType = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_INPUT_SUBSCRIBER_TYPE)
    payment_deadline: int = Field(description=OpenAPIFieldDescription.PAYMENT_DEADLINE)
    deadline_unit_time: str = Field(description=OpenAPIFieldDescription.PAYMENT_UNIT_DEADLINE)
    subscribed_power: str = Field(description=OpenAPIFieldDescription.SUBSCRIBED_POWER)
    power_of_energy: str = Field(description=OpenAPIFieldDescription.POWER_OF_ENERGY)
    status: str = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_INPUT_STATUS)
    previous_status: Optional[str] = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_INPUT_PREVIOUS_STATUS)
    level: SubscriptionLevel = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_INPUT_LEVEL)
    previous_level: Optional[str] = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_INPUT_PREVIOUS_LEVEL)
    invoicing_frequency: int = Field(description=OpenAPIFieldDescription.INVOICING_FREQUENCY)
    agency: Agency = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_INPUT_AGENCY)
    home_infos: HomeInfos = Field(description=OpenAPIFieldDescription.HomeInfos)
    is_blocked_pricing: bool = Field(
        description=OpenAPIFieldDescription.IS_BLOCKED_PAYED,
        default=False,
    )

class ContractInfoDto(ContractInfo):
    pricing: Pricing = Field(description=OpenAPIFieldDescription.PRICING)

class ContractInfoInput(ContractInfo):
    delivery_point: DeliveryPoint = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_INPUT_DELIVERY_POINT)


class ContractInfoOutput(ContractInfoDto, metaclass=AllOptional):
    delivery_point: DeliveryPoint

class ContractInfoInputUpdate(ContractInfoDto):
    delivery_point: DeliveryPointUpdate = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_INPUT_DELIVERY_POINT)

    class Config:
        hide_fields = {
            "pricing",
            "subscription_type",
            "deadline_unit_time",
            "payment_deadline",
            "agency",
            "subscribed_power",
            "power_of_energy",
        }

class ContractSchema(ContractInfoInput):
    customer_number: str

class BaseContactDto(BaseModel):
    id: int
    opening_date: datetime = Field(description=OpenAPIFieldDescription.CONTRACT_OPENING_DATE)
    closing_date: datetime = Field(description=OpenAPIFieldDescription.CONTRACT_CLOSING_DATE)
    created_at: datetime = Field(description=OpenAPIFieldDescription.CONTRACT_CREATED_AT)
    updated_at: datetime = Field(description=OpenAPIFieldDescription.CONTRACT_UPDATED_AT)
    deleted_at: datetime = Field(description=OpenAPIFieldDescription.CONTRACT_CLOSING_DATE)
    is_activated: bool = Field(description=OpenAPIFieldDescription.IS_ACTIVATED)
    contract_number: str = Field(description=OpenAPIFieldDescription.CONTRACT_UID)
    customer_number: str


class ContractDto(BaseContactDto, metaclass=AllOptional):
    infos: ContractInfoOutput = Field(description=OpenAPIFieldDescription.CONTRACT_OUTPUT_INFO)

class ContractDtoUpdate(BaseContactDto, metaclass=AllOptional):
    infos: ContractInfoInputUpdate = Field(description=OpenAPIFieldDescription.CONTRACT_OUTPUT_INFO)

class ContractDtoWithPagination(BaseModel):
    count: int
    total: int
    offset: int
    limit: int
    data: List[ContractDto]

class CustomerStatus(Enum):
    ACTIVE = "Activé"
    PENDED = "Suspendu"
    CLOSED = "Clôturé"
    CREATED = "Créé"
    INCOMPLETE = "Incomplet"
    WAITING_FOR_ACTIVATION = "En attente d’activation"

class ContractDtoQueryParams(BaseModel):
    customer_number: Optional[str] = Field(description=OpenAPIFieldDescription.CUSTOMER_ID)
    contract_number: Optional[str] = Field(description=OpenAPIFieldDescription.CONTRACT_UID)
    status: Optional[CustomerStatus] = Field(description=OpenAPIFieldDescription.STATUS)

class PricingDto(Pricing, metaclass=AllOptional):
    pass

class Invoice(BaseModel):
    invoice_number: Optional[str] = Field(description=OpenAPIFieldDescription.INVOICE_NUMBER)
    invoice_date: Optional[str] = Field(description=OpenAPIFieldDescription.INVOICE_DATE)
    last_index_value: Optional[str] = Field(description=OpenAPIFieldDescription.LAST_INDEX_VALUE)
    last_power_recharged: Optional[str] = Field(description=OpenAPIFieldDescription.LAST_POWER_RECHARGED)
    power_recharged: Optional[str] = Field(description=OpenAPIFieldDescription.POWER_RECHARGED)
    index_value: Optional[str] = Field(description=OpenAPIFieldDescription.INDEX_VALUE)
    total_power_consumed: Optional[str] = Field(description=OpenAPIFieldDescription.TOTAL_POWER_CONSUMED)
    total_power_recharged: Optional[str] = Field(description=OpenAPIFieldDescription.TOTAL_POWER_RECHARGED)
    total_amount_ht: Optional[float] = Field(description=OpenAPIFieldDescription.TOTAL_AMOUNT_HT)
    total_amount_ttc: Optional[float] = Field(description=OpenAPIFieldDescription.TOTAL_AMOUNT_TTC)
    tva: Optional[str] = Field(description=OpenAPIFieldDescription.TVA)
    payment_deadline: Optional[str] = Field(description=OpenAPIFieldDescription.PAYMENT_DEADLINE)
    amount_paid: Optional[float] = Field(description=OpenAPIFieldDescription.AMOUNT_PAID)
    remaining_amount: Optional[float] = Field(description=OpenAPIFieldDescription.REMAINING_AMOUNT)
    status: Optional[str] = Field(description=OpenAPIFieldDescription.INVOICE_STATUS)
    type: Optional[str] = Field(description=OpenAPIFieldDescription.INVOICE_TYPE)

class ContractInvoiceDetails(BaseModel):
    warning_message: Optional[str]
    consumption_estimated: Optional[str]
    subscription_type: Optional[str] = Field(description=OpenAPIFieldDescription.CONTRACT_SUBSCRIBER_TYPE_NAME)
    payment_deadline: Optional[int] = Field(description=OpenAPIFieldDescription.PAYMENT_DEADLINE)
    subscribed_power: Optional[str] = Field(description=OpenAPIFieldDescription.SUBSCRIBED_POWER)
    delivery_point: DeliveryPoint = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_INPUT_DELIVERY_POINT)
    is_bocked_payment: bool = Field(description=OpenAPIFieldDescription.IS_BLOCKED_PAYED)
    agency: Agency = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_INPUT_AGENCY)
    invoice: List[Invoice]

class ContactContracts(ContactInfosOutput):
    contracts: List[ContractDto]

class ContractDetails(BaseModel):
    contract: List[ContractDto]

class InvoiceDetails(BaseModel):
    contract_number: str
    invoice: List[Invoice]

class ContractInvoiceParams(BaseModel):
    contract_number: Optional[str] = Field(description=OpenAPIFieldDescription.CONTRACT_UID)
    invoice_date_start: Optional[date] = Field(description=OpenAPIFieldDescription.INVOICE_DATE_START)
    invoice_date_end: Optional[date] = Field(description=OpenAPIFieldDescription.INVOICE_DATE_END)

class ContractInvoiceForBillingService(BaseModel):
    contract_number: List[str] = Field(description=OpenAPIFieldDescription.CONTRACT_UID)
    invoice_date_start: Optional[str] = Field(description=OpenAPIFieldDescription.INVOICE_DATE_START)
    invoice_date_end: Optional[str] = Field(description=OpenAPIFieldDescription.INVOICE_DATE_END)

class ContactDtoForBillingService(ContractDto):
    contact: ContactInfosOutput

class ContactWithContractAndPricing(BaseModel):
    contact_contract: List[ContactDtoForBillingService]