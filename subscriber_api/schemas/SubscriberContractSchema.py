from datetime import date
from typing import Optional, Dict, List

from pydantic import BaseModel, Field

from subscriber_api.constant import OpenAPIFieldDescription


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


class SubscriberContractInfoInputTest(BaseModel):
    subscriber_type: int = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_INPUT_SUBSCRIBER_TYPE)
    power_of_energy: str = Field(description=OpenAPIFieldDescription.POWER_OF_ENERGY)
    status: int = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_INPUT_STATUS)
    previous_status: int | None = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_INPUT_PREVIOUS_STATUS)
    level: int = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_INPUT_LEVEL)
    previous_level: int | None = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_INPUT_PREVIOUS_LEVEL)
    invoicing_frequency: int = Field(description=OpenAPIFieldDescription.INVOICING_FREQUENCY)
    delivery_point: int = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_INPUT_DELIVERY_POINT)
    metric_number: str = Field(description=OpenAPIFieldDescription.METRIC_NUMBER)
    agency: int = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_INPUT_AGENCY)

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
    delay_penalty_rate: int = Field(description=OpenAPIFieldDescription.DELAY_PENALTY_RATE)

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


class InvoicingFrequency(BaseModel):
    id: int
    frequency_name: str = Field(description=OpenAPIFieldDescription.FREQUENCY_NAME)
    frequency_shortname: str = Field(description=OpenAPIFieldDescription.FREQUENCY_SHORTNAME)

    class Config:
        orm_mode = True


class EnergyDeparture(BaseModel):
    infos: dict = Field(description=OpenAPIFieldDescription.ENERGY_DEPARTURE_INFO)
    address: dict = Field(description=OpenAPIFieldDescription.ADDRESS)
    created_at: date = Field(description=OpenAPIFieldDescription.CREATED_AT)

    class Config:
        orm_mode = True


class TransformerInfos(BaseModel):
    id: int
    infos: dict = Field(description=OpenAPIFieldDescription.TRANSFORMER_INFO)
    energy_departure: EnergyDeparture = Field(description=OpenAPIFieldDescription.ENERGY_DEPARTURE)
    address: dict = Field(description=OpenAPIFieldDescription.ADDRESS)
    created_at: date = Field(description=OpenAPIFieldDescription.CREATED_AT)
    city_name: str = Field(description=OpenAPIFieldDescription.CITY_NAME)
    prefecture_name: str = Field(description=OpenAPIFieldDescription.PREFECTURE_NAME)
    admin_region_name: str = Field(description=OpenAPIFieldDescription.ADMIN_REGION_NAME)
    natural_region_name: str = Field(description=OpenAPIFieldDescription.NATURAL_REGION_NAME)

    class Config:
        orm_mode = True


class ConnectionPoint(BaseModel):
    id: int | None
    transformer_infos: TransformerInfos = Field(description=OpenAPIFieldDescription.TRANSFORMER_INFO)
    city_name: str = Field(description=OpenAPIFieldDescription.CITY_NAME)
    prefecture_name: str = Field(description=OpenAPIFieldDescription.PREFECTURE_NAME)
    admin_region_name: str = Field(description=OpenAPIFieldDescription.ADMIN_REGION_NAME)
    natural_region_name: str = Field(description=OpenAPIFieldDescription.NATURAL_REGION_NAME)

    class Config:
        orm_mode = True


class DeliveryPointRef(BaseModel):
    id: int
    infos: dict = Field(description=OpenAPIFieldDescription.DELIVERY_POINT)
    connection_point: ConnectionPoint = Field(description=OpenAPIFieldDescription.CONNECTION_POINT)
    address: dict = Field(description=OpenAPIFieldDescription.ADDRESS)
    created_at: date = Field(description=OpenAPIFieldDescription.DELIVERY_POINT_CREATED_AT)
    updated_at: date = Field(description=OpenAPIFieldDescription.DELIVERY_POINT_UPDATED_AT)
    city_name: str = Field(description=OpenAPIFieldDescription.CITY_NAME)
    prefecture_name: str = Field(description=OpenAPIFieldDescription.PREFECTURE_NAME)
    admin_region_name: str = Field(description=OpenAPIFieldDescription.ADMIN_REGION_NAME)
    natural_region_name: str = Field(description=OpenAPIFieldDescription.NATURAL_REGION_NAME)

    class Config:
        orm_mode = True


class SubscriberContractInfoOutputTest(BaseModel):
    subscriber_type: str = Field(description=OpenAPIFieldDescription.SUBSCRIBER_TYPE)
    power_of_energy: str = Field(description=OpenAPIFieldDescription.POWER_OF_ENERGY)
    status: str = Field(description=OpenAPIFieldDescription.STATUS)
    previous_status: str | None = Field(description=OpenAPIFieldDescription.PREVIOUS_STATUS)
    level: SubscriptionLevel = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_OUTPUT_LEVEL)
    previous_level: SubscriptionLevel = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_OUTPUT_PREVIOUS_LEVEL)
    invoicing_frequency: InvoicingFrequency = Field(description=OpenAPIFieldDescription.INVOICING_FREQUENCY)
    delivery_point: DeliveryPoint = Field(description=OpenAPIFieldDescription.DELIVERY_POINT)
    metric_number: str = Field(description=OpenAPIFieldDescription.METRIC_NUMBER)
    agency: Agency = Field(description=OpenAPIFieldDescription.AGENCY)

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
    opening_date: date | None = Field(description=OpenAPIFieldDescription.CONTRACT_OPENING_DATE)
    closing_date: date | None = Field(description=OpenAPIFieldDescription.CONTRACT_CLOSING_DATE)
    created_at: date | None = Field(description=OpenAPIFieldDescription.CONTRACT_CREATED_AT)
    updated_at: date | None = Field(description=OpenAPIFieldDescription.CONTRACT_UPDATED_AT)
    deleted_at: date | None = Field(description=OpenAPIFieldDescription.CONTRACT_CLOSING_DATE)
    is_activated: bool | None = Field(description=OpenAPIFieldDescription.IS_ACTIVATED)
    contract_uid: str | None = Field(description=OpenAPIFieldDescription.CONTRACT_UID)

    class Config:
        orm_mode = True


class ContractDtoIncoming(BaseModel):
    id: int | None
    customer_number: str | None = Field(description=OpenAPIFieldDescription.CUSTOMER_ID)
    contract_number: str | None = Field(description=OpenAPIFieldDescription.CONTRACT_UID)


class ContractDtoForBillingMicroService(BaseModel):
    subscriber_type: SubscriptionType | None = Field(description=OpenAPIFieldDescription.SUBSCRIBER_TYPE)
    power_of_energy: str | None = Field(description=OpenAPIFieldDescription.POWER_OF_ENERGY)
    status: str | None = Field(description=OpenAPIFieldDescription.STATUS)
    invoicing_frequency: str | None = Field(description=OpenAPIFieldDescription.INVOICING_FREQUENCY)
    delivery_point: DeliveryPoint | None = Field(description=OpenAPIFieldDescription.DELIVERY_POINT)
    metric_number: str | None = Field(description=OpenAPIFieldDescription.METRIC_NUMBER)
    level: SubscriptionLevel = Field(description=OpenAPIFieldDescription.CONTRACT_INFO_OUTPUT_LEVEL)
    pricing: List[Pricing] | None = Field(description=OpenAPIFieldDescription.PRICING)
    dunning: List[Dunning] | None = Field(description=OpenAPIFieldDescription.DUNNING)
    tracking_type: TrackingType = Field(description=OpenAPIFieldDescription.TRACKING_TYPE, )
