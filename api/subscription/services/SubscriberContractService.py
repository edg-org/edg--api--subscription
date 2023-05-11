import json
import logging
from collections import Counter
from datetime import datetime
from typing import List, Coroutine, Any

from fastapi import Depends
from fastapi.encoders import jsonable_encoder

from api.contact.models.SubscriberContractModel import SubscriberContract
from api.contact.schemas.pydantic.ContactsSchema import ContactOutputDto

from api.contact.services.ContactsService import ContactsService
from api.subscription.exceptions import ContractNotFound, DeleteContractException, ContactNotFound, \
    EditContactWhileNotOwner, ContractDisabled, ContractExist, ContractStatusError, RepeatingDeliveryPoint, \
    ContractLevelError, ContractOrContactNotFound, StatusErrorWhenCurrentStatusIsEqualInitial, \
    StatusErrorWhenCurrentStatusIsEqualEdited, ContractIsAlreadyActivated

from api.subscription.repositories.SubscriberContractRepository import SubscriberContractRepository
from api.subscription.schemas.SubscriberContractSchema import SubscriberContractSchema, ContractDtoIncoming, \
    ContractDto, ContractDtoWithPagination, BillingDto
from api.subscription.services.GuidGenerator import GuidGenerator
from api.subscription.services.RequestMaster import RequestMaster
from api.subscription.utilis.Status import ContractStatus


class SubscriberContactService:
    subscriber_contract_repository: SubscriberContractRepository
    contact_service: ContactsService

    def __init__(self,
                 subscriber_contract_repository: SubscriberContractRepository = Depends(),
                 contact_service: ContactsService = Depends()
                 ) -> None:
        self.subscriber_contract_repository = subscriber_contract_repository
        self.contact_service = contact_service

    def buildContractDto(self, contract: SubscriberContract) -> ContractDto:
        return ContractDto(
            id=contract.id,
            infos=contract.infos,
            customer_id=contract.customer_id,
            opening_date=contract.opening_date,
            closing_date=contract.closing_date,
            created_at=contract.created_at,
            updated_at=contract.updated_at,
            deleted_at=contract.deleted_at,
            is_activated=contract.is_activated,
            contract_number=contract.contract_number
        )

    def buildContractDtoWithPagination(self, contracts: List[ContractDto], offset: int, limit: int, count: int):
        total: int = len(contracts)
        offset: int
        limit: int
        return ContractDtoWithPagination(
            count=count,
            total=total,
            offset=offset,
            limit=limit,
            data=contracts
        )

    def create_contract(self, contract_schema: List[SubscriberContractSchema]) -> List[ContractDto]:
        """
        This service has a purpose to create a new contract
        :param contract_schema: the data model to fill
        :return: return a created object from db SubscriberContract
        """
        # Transform contract_schema to a list
        contract_schema = json.dumps([contract.dict() for contract in contract_schema])
        contract_schema = json.loads(contract_schema)

        # Check if there are repeating delivery point, if true, then the len of delivery_points will be different
        # to the len of contract_schema
        # if the flag is true, then we set pricing and dunning to null
        delivery_points_on_number = set()
        delivery_point_on_metric_number = set()
        for contract in contract_schema:
            delivery_points_on_number.add(contract["delivery_point"]['number'])
            delivery_point_on_metric_number.add(contract["delivery_point"]['metric_number'])
            if not contract['is_bocked_payment']:
                contract['pricing'] = None
                contract['dunning'] = None
        if (len(delivery_points_on_number) != len(contract_schema) or
                len(delivery_point_on_metric_number) != len(contract_schema)):
            raise RepeatingDeliveryPoint

        contracts: List[SubscriberContract] = [self.check_save_business_logic(c) for c in contract_schema]
        self.contractUID(self.contact_service.get_contact_by_id_for_client(23),contract_schema)
        # contracts = self.subscriber_contract_repository.create_contract(contracts)
        return [self.buildContractDto(c) for c in contracts]

    def contractUID(self, contact: ContactOutputDto, contract_schemas: List[SubscriberContractSchema]) \
            -> str:
        # get contact from db if exist
        amount_contract = 0
        if contact is not None:
            amount_contract = self.subscriber_contract_repository.count_contract_by_contact_number(
                contact.customer_number)
        # check for repeating contract for given customer id in contract_schemas variable
        # contract_schemas = json.dumps([contract.dict() for contract in contract_schemas])
        # contract_schemas = json.loads(contract_schemas)
        customer_count = Counter(item['customer_id'] for item in contract_schemas)
        customer_repeat = dict()
        value_to_return = []
        for i, (customer, count) in enumerate(customer_count.items()):
            customer_repeat['customer_id'] = customer
            customer_repeat['count'] = count
            value_to_return.append(customer_repeat)
        logging.error("mmm %s", value_to_return)
        contact = jsonable_encoder(contact)
        return "C" + str(abs(hash(contact['infos']['identity']['pid'])) % (10 ** 7))

    def check_save_business_logic(self, contract_schema: SubscriberContractSchema) -> SubscriberContract:
        """
        This service verify if the contact and contract is already exist and the contract is not assign to any
        delivery point
        :param contract_schema:
        :return: SubscriberContract
        """
        # contract_schema.infos = json.loads(contract_schema.infos.json())
        # logging.warning(f"type of contract schema %s", type(contract_schema))
        contact: ContactOutputDto = self.contact_service.get_contact_by_id_for_client(contract_schema['customer_id'])

        contract_exist = self.subscriber_contract_repository \
            .get_contract_by_delivery_point_on_number(
            contract_schema['delivery_point']['number']
        )

        if contract_exist is not None:
            raise ContractExist(" number " + contract_exist.infos['delivery_point']['number'])

        contract_exist = self.subscriber_contract_repository.get_contract_by_delivery_point_on_metric_number(
            contract_schema['delivery_point']['metric_number']
        )

        if contract_exist is not None:
            raise ContractExist(" metric number " + contract_exist.infos['delivery_point']['metric_number'])

        if contract_schema['status'] == contract_schema['previous_status']:
            raise ContractStatusError

        if contract_schema['level']['name'] == contract_schema['previous_level']:
            raise ContractLevelError

        contact = jsonable_encoder(contact)
        # logging.error("msgaga %s", contact)

        return SubscriberContract(
            infos=contract_schema,
            customer_id=contract_schema['customer_id'],
            # contract_number=GuidGenerator.contractUID(contact['infos']['identity']['pid'], ""),
        )

    def update_contract(self, contract_number: str, contract_schema: SubscriberContractSchema) -> ContractDto:
        """
        This service update an existing contract from the database
        :param contract_number: contract unique number
        :param contract_schema: request body, the data model from db
        :return: return an updated contract's information associated to delivery point and customer_id
        """

        contract_schema = jsonable_encoder(contract_schema)
        logging.error(contract_schema['status'])
        # Previous status should be different to current status
        if contract_schema['status'] == contract_schema['previous_status']:
            raise ContractStatusError

        contract_exist: SubscriberContract = self.subscriber_contract_repository \
            .get_contract_by_contract_uid(contract_number)
        # if the contract does not exist, so we throw an exception
        if contract_exist is None:
            raise ContractNotFound

        if contract_exist.deleted_at is not None:
            raise ContractDisabled

        # check if the contact exist
        contact: ContactOutputDto = self.contact_service. \
            get_contact_by_id_for_client(contract_schema['customer_id'])
        if contact is None:
            raise ContactNotFound

        # if the contract exist, but not associate to the contact, then we raise an exception
        if contract_exist is not None and contact.id != contract_exist.customer_id:
            raise EditContactWhileNotOwner

        # Verify in the contract exist from the submitted schema

        delivery_point_associate_to_contract: SubscriberContract = self.subscriber_contract_repository. \
            get_contract_by_delivery_point_on_number(contract_schema['delivery_point']['number'])
        if (delivery_point_associate_to_contract is not None and
                delivery_point_associate_to_contract.customer_id != contact.id):
            raise EditContactWhileNotOwner

        # Is the contract activate, if not, we cannot apply any edit operation on it
        # if contract_exist.opening_date is None:
        #    raise ContractDisabled
        # If the closing date is set that mean that the contract is resigned
        if contract_exist.closing_date is not None:
            raise ContractDisabled

        # check status logic
        contract_exist = self.contract_status_logic(contract_exist, contract_schema['status'])
        # Subscription type and delivery point is immutable
        contract_schema['previous_status'] = contract_exist.infos['status']
        contract_schema['subscription_type'] = contract_exist.infos['subscription_type']
        contract_schema['delivery_point'] = contract_exist.infos['delivery_point']

        contract: SubscriberContract = self.subscriber_contract_repository.update_contract(
            SubscriberContract(
                id=contract_exist.id,
                infos=contract_schema,
                customer_id=contract_exist.customer_id,
                opening_date=contract_exist.opening_date,
                closing_date=contract_exist.closing_date,
                created_at=contract_exist.created_at,
                updated_at=datetime.now().replace(microsecond=0),
                deleted_at=contract_exist.deleted_at,
                is_activated=contract_exist.is_activated,
                contract_number=contract_exist.contract_number,
                attachment=contract_exist.attachment)
        )
        return self.buildContractDto(contract)

    def activate_contract(self, contract_number: str) -> ContractDto:
        """
        This service update contract's status by contract uid
        :param contract_number:
        :return:
        """
        contract: SubscriberContract = self.subscriber_contract_repository.get_contract_by_contract_uid_for_update(
            contract_number
        )
        if contract.deleted_at is not None:
            raise ContractDisabled
        if contract is None:
            raise ContractNotFound
        if not contract.is_activated:
            contract.opening_date = datetime.now().replace(microsecond=0)
            contract.updated_at = datetime.now().replace(microsecond=0)
            contract.is_activated = True

        else:
            raise ContractIsAlreadyActivated

        contract.infos['previous_status'] = contract.infos['status']
        contract.infos['status'] = ContractStatus.ACTIVE
        contract = self.subscriber_contract_repository.update_contract(contract)

        return self.buildContractDto(contract)

    def contract_status_logic(self, contract: SubscriberContract | None, status: str) -> SubscriberContract:
        # check contract status
        # if the status is ContractStatus.INITIAL, so it can't change to ContractStatus.CREATED
        # or ContractStatus.INCOMPLETE
        if contract is None:
            raise ContractNotFound
        if (contract.infos['status'] == ContractStatus.ACTIVE and
                status in [ContractStatus.CREATED, ContractStatus.INCOMPLETE]):
            raise StatusErrorWhenCurrentStatusIsEqualInitial
        # if the status is ContractStatus.EDITED, so it can't change to ContractStatus.CREATED
        if (contract.infos['status'] == ContractStatus.PENDED
            or contract.infos['status'] == ContractStatus.INCOMPLETE
        ) and status == ContractStatus.CREATED:
            raise StatusErrorWhenCurrentStatusIsEqualEdited

        if contract.infos['status'] == ContractStatus.ACTIVE:
            contract.is_activated = True
        return contract

    def delete_contract(self, contract_number: str) -> None:
        """
        This service is used to delete the contract by the contract delivery point
        :param contract_number:
        :return: None
        """
        contract: SubscriberContract = self.subscriber_contract_repository.get_contract_by_contract_uid(
            contract_number
        )
        if contract is None:
            raise DeleteContractException
        else:
            contract.deleted_at = datetime.now().replace(microsecond=0)
            contract.is_activated = False
            contract.closing_date = datetime.now().replace(microsecond=0)

        self.subscriber_contract_repository.delete_contract(contract)

    def get_contract_by_customer_id_for_client(self, customer_id: int, offset: int, limit: int) \
            -> List[ContractDto]:
        """
        This service is used  to filter activated contract by costumer id
        :param customer_id:
        :param offset: start page
        :param limit: end page
        :return: throw an error the contract does not exist or return SubscriberContract
         """
        contract: List[SubscriberContract] = self.subscriber_contract_repository \
            .get_contract_by_customer_id_for_client(customer_id, offset, limit)

        if len(contract) == 0:
            raise ContractNotFound

        return [self.buildContractDto(c) for c in contract]

    def get_contract_by_contract_uid(self, contract_number: str) -> ContractDto:
        """
        This service is used to fill activated contract by a specific contract unique number
        :param contract_number: contract unique number
        :return: SubscriberContract or throw an HTTPException error
        """
        contract: SubscriberContract = self.subscriber_contract_repository \
            .get_contract_by_contract_uid(contract_number)
        if contract is None:
            raise ContractNotFound

        return self.buildContractDto(contract)

    def get_contract_by_submitted_params(self, params: ContractDtoIncoming, offset: int,
                                         limit: int) -> ContractDtoWithPagination:
        """
        This function fileter a contract by submitted params
        :param offset:
        :param limit:
        :param params:
        :return:
        """
        # logging.warning("excluded id", params.dict(exclude_none=True).)

        contracts: List[SubscriberContract] = self.subscriber_contract_repository. \
            get_contract_by_submitted_params(params, offset, limit)
        if len(contracts) == 0:
            raise ContractNotFound
        return self.buildContractDtoWithPagination(contracts, offset, limit,
                                                   self.subscriber_contract_repository.count_contract(params))

    def get_contract_by_contact_number(self, contact_number: str, offset: int, limit: int) -> ContractDtoWithPagination:
        """
        This method get contract information by contact number
        :param contact_number:
        :param offset:
        :param limit:
        :return: ContractDtoWithPagination
        """
        contracts = self.subscriber_contract_repository.get_contract_by_contact_number(contact_number)
        if len(contracts) == 0:
            raise ContractNotFound
        contracts = [self.buildContractDto(c) for c in contracts]
        return self.buildContractDtoWithPagination(
            contracts, offset, limit, self.subscriber_contract_repository.
            count_contract_by_contact_number(contact_number)
        )

    def get_contracts_by_contact_number(self, contact_number) -> List[ContractDto]:
        """
        Return all contract by customer number
        :param contact_number:
        :return:  List[ContractDto] or empty List
        """
        contracts = self.subscriber_contract_repository.get_contract_by_contact_number(contact_number)
        if len(contracts) == 0:
            raise ContractNotFound
        return [self.buildContractDto(c) for c in contracts]

    def get_billing(self, number) -> BillingDto | None:
        """
        Request referential system to get a billing information
        :param number:
        :return: BillingDto
        """
        # Check if contact exist
        contract: SubscriberContract = self.subscriber_contract_repository. \
            get_contract_by_contract_uid(number)
        if contract is None:
            raise ContractNotFound
        # Do request to the external service and get data
        return RequestMaster. \
            get_billing_info(1, "http://localhost:8082/pricing", "")
