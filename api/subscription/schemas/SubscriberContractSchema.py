from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from api.subscription.constant import OpenAPIFieldDescription


class SubscriptionLevel(BaseModel):
    name: str = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_LEVEL_NAME)
    payment_mode: List[str] = Field(description=OpenAPIFieldDescription.PAYMENT_MODE_NAME)


class SubscriptionLevelIncomingFilter(BaseModel):
    name: str | None = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_LEVEL_NAME)
    payment_mode: str | None = Field(description=OpenAPIFieldDescription.PAYMENT_MODE_NAME)


class Agency(BaseModel):
    name: str = Field(description=OpenAPIFieldDescription.AGENCY_NAME)
    code: str = Field(description=OpenAPIFieldDescription.AGENCY_CODE)
    tel: str = Field(description=OpenAPIFieldDescription.AGENCY_TEL)
    email: str = Field(description=OpenAPIFieldDescription.AGENCY_EMAIL)

    class Config:
        orm_mode = True


class SubscriptionType(BaseModel):
    code: int = Field(description=OpenAPIFieldDescription.SUBSCRIPTION_CODE)
    name: str = Field(description=OpenAPIFieldDescription.SUBSCRIPTION_NAME)

    class Config:
        orm_mode = True


class DeliveryPoint(BaseModel):
    number: str = Field(description=OpenAPIFieldDescription.DELIVERY_NUMBER)
    metric_number: str = Field(description=OpenAPIFieldDescription.METRIC_NUMBER)

    class Config:
        orm_mode = True


class Equipment(BaseModel):
    total: int = Field(description=OpenAPIFieldDescription.AMOUNT_EQUIPMENT)
    details: List[str] = Field(description=OpenAPIFieldDescription.EQUIPMENT_LIST)

    class Config:
        orm_mode = True


class HomeInfos(BaseModel):
    surface: int = Field(description=OpenAPIFieldDescription.SURFACE)
    occupier_number: int = Field(description=OpenAPIFieldDescription.OCCUPIER_NUMBER)
    equipment: Equipment = Field(description=OpenAPIFieldDescription.EQUIPMENT)

    class Config:
        orm_mode = True


class Pricing(BaseModel):
    slice_name: str = Field(description=OpenAPIFieldDescription.SLICE_NAME)
    lower_index: int = Field(description=OpenAPIFieldDescription.LOWER_INDEX)
    upper_index: int = Field(description=OpenAPIFieldDescription.UPPER_INDEX)
    unit_price: int = Field(description=OpenAPIFieldDescription.UNIT_PRICE)

    class Config:
        orm_mode = True


class Dunning(BaseModel):
    name: str = Field(description=OpenAPIFieldDescription.DUNNING_NAME)
    rank: int = Field(description=OpenAPIFieldDescription.DUNNING_RANK)
    payment_deadline: int = Field(description=OpenAPIFieldDescription.PAYMENT_DEADLINE)
    delay_penality_rate: int = Field(description=OpenAPIFieldDescription.DELAY_PENALTY_RATE)

    class Config:
        orm_mode = True


class TrackingType(BaseModel):
    code: int = Field(description=OpenAPIFieldDescription.TRACKING_CODE)
    name: str = Field(description=OpenAPIFieldDescription.TRACKING_NAME)


class SubscriberContractInfoInput(BaseModel):
    subscription_type: SubscriptionType = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_INPUT_SUBSCRIBER_TYPE)
    payment_deadline: int = Field(description=OpenAPIFieldDescription.PAYMENT_DEADLINE)
    deadline_unit_time: str = Field(description=OpenAPIFieldDescription.PAYMENT_UNIT_DEADLINE)
    subscribed_power: str = Field(description=OpenAPIFieldDescription.SUBSCRIBED_POWER)
    power_of_energy: str = Field(description=OpenAPIFieldDescription.POWER_OF_ENERGY)
    status: str = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_INPUT_STATUS)
    previous_status: str | None = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_INPUT_PREVIOUS_STATUS)
    level: SubscriptionLevel = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_INPUT_LEVEL)
    previous_level: str | None = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_INPUT_PREVIOUS_LEVEL)
    invoicing_frequency: int = Field(description=OpenAPIFieldDescription.INVOICING_FREQUENCY)
    delivery_point: DeliveryPoint = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_INPUT_DELIVERY_POINT)
    agency: Agency = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_INPUT_AGENCY)
    home_infos: HomeInfos = Field(description=OpenAPIFieldDescription.HomeInfos)
    customer_id: int = Field(description=OpenAPIFieldDescription.CUSTOMER_ID)
    is_bocked_payment: bool = Field(description=OpenAPIFieldDescription.IS_BLOCKED_PAYED, default=False)
    pricing: List[Pricing] | None = Field(description=OpenAPIFieldDescription.PRICING)
    dunning: List[Dunning] | None = Field(description=OpenAPIFieldDescription.DUNNING)
    tracking_type: TrackingType = Field(description=OpenAPIFieldDescription.TRACKING_TYPE, )

    class Config:
        orm_mode = True


class SubscriberContractInfoOutput(SubscriberContractInfoInput):
    class Config:
        orm_mode = True


class AgencyIncomingFilter(BaseModel):
    name: str | None = Field(description=OpenAPIFieldDescription.AGENCY_NAME)
    code: str | None = Field(description=OpenAPIFieldDescription.AGENCY_CODE)
    tel: str | None = Field(description=OpenAPIFieldDescription.AGENCY_TEL)
    email: str | None = Field(description=OpenAPIFieldDescription.AGENCY_EMAIL)

    class Config:
        orm_mode = True


class SubscriberContractInfoForFilter(BaseModel):
    status: str | None = Field(description=OpenAPIFieldDescription.STATUS)
    previous_status: str | None = Field(description=OpenAPIFieldDescription.PREVIOUS_STATUS)
    invoicing_frequency: str | None = Field(description=OpenAPIFieldDescription.INVOICING_FREQUENCY)
    subscription_type_name: str | None = Field(description=OpenAPIFieldDescription.SUBSCRIBER_TYPE)
    level_name: str | None = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_LEVEL_NAME)
    tracking_name: str | None = Field(description=OpenAPIFieldDescription.TRACKING_NAME)

    class Config:
        orm_mode = True


class SubscriberContractSchema(SubscriberContractInfoInput):
    pass


class ContractDto(BaseModel):
    id: int | None
    infos: SubscriberContractInfoOutput | None = Field(description=OpenAPIFieldDescription.CONTRACT_OUTPUT_INFO)
    opening_date: datetime | None = Field(description=OpenAPIFieldDescription.CONTRACT_OPENING_DATE)
    closing_date: datetime | None = Field(description=OpenAPIFieldDescription.CONTRACT_CLOSING_DATE)
    created_at: datetime | None = Field(description=OpenAPIFieldDescription.CONTRACT_CREATED_AT)
    updated_at: datetime | None = Field(description=OpenAPIFieldDescription.CONTRACT_UPDATED_AT)
    deleted_at: datetime | None = Field(description=OpenAPIFieldDescription.CONTRACT_CLOSING_DATE)
    is_activated: bool | None = Field(description=OpenAPIFieldDescription.IS_ACTIVATED)
    contract_number: str | None = Field(description=OpenAPIFieldDescription.CONTRACT_UID)

    class Config:
        orm_mode = True


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


class ContractDtoIncoming(BaseModel):
    customer_number: str | None = Field(description=OpenAPIFieldDescription.CUSTOMER_ID)
    contract_number: str | None = Field(description=OpenAPIFieldDescription.CONTRACT_UID)
    status: CustomerStatus | None = Field(description=OpenAPIFieldDescription.STATUS)


class BillingDto(BaseModel):
    maximum_dunning: int | None = Field(description=OpenAPIFieldDescription.DUNNING)
    subscription_type: str | None = Field(description=OpenAPIFieldDescription.SUBSCRIBER_TYPE)
    payment_deadline: int | None = Field(description=OpenAPIFieldDescription.PAYMENT_DEADLINE)
    deadline_unit_time: str | None = Field(description=OpenAPIFieldDescription.PAYMENT_UNIT_DEADLINE)
    invoicing_frequency: int | None = Field(description=OpenAPIFieldDescription.INVOICING_FREQUENCY)
    prime: int | None = Field(description=OpenAPIFieldDescription.PRIME)
    pricing: List[Pricing] | None = Field(description=OpenAPIFieldDescription.PRICING)
    dunning: List[Dunning] | None = Field(description=OpenAPIFieldDescription.DUNNING)
