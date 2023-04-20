import json
import logging
import random
from datetime import date
from typing import List, Optional

from fastapi import Depends
from fastapi.encoders import jsonable_encoder

from api.models.ContactsModel import Contacts
from subscriber_api.models.SubscriberContractModel import SubscriberContract
from api.services.ContactsService import ContactsService
from subscriber_api.exceptions import ContractNotFound, DeleteContractException, ContactNotFound, \
    EditContactWhileNotOwner, ContractDisabled, ContractExist, ContractStatusError, RepeatingDeliveryPoint, \
    ContractLevelError

from subscriber_api.repositories.SubscriberContractRepository import SubscriberContractRepository
from subscriber_api.schemas.SubscriberContractSchema import SubscriberContractSchema, ContractDtoIncoming, \
    SubscriberContractInfoForFilter, Agency, AgencyIncomingFilter, ContractDto, SubscriptionLevel, \
    SubscriptionLevelIncomingFilter, ContractDtoForBillingMicroService, SubscriptionType
from subscriber_api.services.GuidGenerator import GuidGenerator


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
            contract_uid=contract.contract_uid
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
        delivery_points = set()
        for contract in contract_schema:
            delivery_points.add(contract["delivery_point"]['number'])
            if not contract['is_bocked_payment']:
                contract['pricing'] = None
                contract['dunning'] = None
        if len(delivery_points) != len(contract_schema):
            raise RepeatingDeliveryPoint

        contract: List[SubscriberContract] = [self.check_save_business_logic(c) for c in contract_schema]
        contract = self.subscriber_contract_repository.create_contract(contract)
        return [self.buildContractDto(c) for c in contract]

    def check_save_business_logic(self, contract_schema: SubscriberContractSchema) -> SubscriberContract:
        """
        This service verify if the contact and contract is already exist and the contract is not assign to any
        delivery point
        :param contract_schema:
        :return: SubscriberContract
        """
        # contract_schema.infos = json.loads(contract_schema.infos.json())
        logging.warning(f"type of contract schema %s", type(contract_schema))
        contact: Contacts = self.contact_service.get_contact_by_id_for_client(contract_schema['customer_id'])
        if contact is None:
            raise ContactNotFound

        contract_exist: SubscriberContract = self.subscriber_contract_repository \
            .get_contract_by_delivery_point(
            contract_schema['delivery_point']['number']
        )
        if contract_exist is not None:
            raise ContractExist

        if contract_schema['status'] == contract_schema['previous_status']:
            raise ContractStatusError

        if contract_schema['level']['name'] == contract_schema['previous_level']:
            raise ContractLevelError

        return SubscriberContract(
            infos=contract_schema,
            customer_id=contract_schema['customer_id'],
            contract_uid=GuidGenerator.contractUID(contact.infos['identity']['pid']),
        )

    def update_contract(self, contract_uid: str, contract_schema: SubscriberContractSchema) -> ContractDto:
        """
        This service update an existing contract from the database
        :param contract_uid: contract unique number
        :param contract_schema: request body, the data model from db
        :return: return an updated contract's information associated to delivery point and customer_id
        """

        contract_schema = jsonable_encoder(contract_schema)
        logging.error(contract_schema['status'])
        # Previous status should be different to current status
        if contract_schema['status'] == contract_schema['previous_status']:
            raise ContractStatusError

        contract_exist: SubscriberContract = self.subscriber_contract_repository \
            .get_contract_by_contract_uid_for_client(contract_uid)
        # if the contract does not exist, so we throw an exception
        if contract_exist is None:
            raise ContractNotFound
        # Don't allow changes the previous status to the current status
        if contract_schema['status'] == contract_schema['previous_status']:
            raise ContractStatusError

        # check if the contact exist
        contact: Contacts = self.contact_service. \
            get_contact_by_id_for_client(contract_schema['customer_id'])
        if contact is None:
            raise ContactNotFound

        # if the contract exist, but not associate to the contact, then we raise an exception
        if contract_exist is not None and contact.id != contract_exist.customer_id:
            raise EditContactWhileNotOwner

        # Verify in the contract exist from the submitted schema

        delivery_point_associate_to_contract: SubscriberContract = self.subscriber_contract_repository. \
            get_contract_by_delivery_point(contract_schema['delivery_point']['number'])
        if delivery_point_associate_to_contract is not None and \
                delivery_point_associate_to_contract.customer_id != contact.id:
            raise EditContactWhileNotOwner

        # Is the contract activate, if not, we cannot apply any edit operation on it
        if contract_exist.opening_date == None:
            raise ContractDisabled
        # If the closing date is set that mean that the contract is resigned
        if contract_exist.closing_date != None:
            raise ContractDisabled

        contract: SubscriberContract = self.subscriber_contract_repository.update_contract(
            SubscriberContract(
                id=contract_exist.id,
                infos=contract_schema,
                customer_id=contract_exist.customer_id,
                opening_date=contract_exist.opening_date,
                closing_date=contract_exist.closing_date,
                created_at=contract_exist.created_at,
                updated_at=date.today(),
                deleted_at=contract_exist.deleted_at,
                is_activated=contract_exist.is_activated,
                contract_uid=contract_exist.contract_uid,
                attachment=contract_exist.attachment)
        )
        return self.buildContractDto(contract)

    def update_contract_status_by_contract_uid(self, contract_uid: str, status: str) -> ContractDto:
        """
        This service update contract's status by contract uid
        :param contract_uid:
        :param status:
        :return:
        """
        contract: SubscriberContract = self.subscriber_contract_repository.get_contract_by_contract_uid_for_client(
            contract_uid
        )
        if contract is None:
            raise ContractNotFound
        if contract.infos['previous_status'] == status:
            raise ContractStatusError
        contract.infos['status'] = status
        contract = self.subscriber_contract_repository.update_contract(contract)
        return self.buildContractDto(contract)

    def update_contract_previous_status_by_contract_uid(self, contract_uid: str, previous_status: str) -> ContractDto:
        """
        This service update contract's previous status by contract uid
        :param contract_uid:
        :param previous_status:
        :return:
        """
        contract: SubscriberContract = self.subscriber_contract_repository.get_contract_by_contract_uid_for_client(
            contract_uid
        )
        if contract is None:
            raise ContractNotFound
        if contract.infos['status'] == previous_status:
            raise ContractStatusError
        contract.infos['previous_status'] = previous_status
        contract = self.subscriber_contract_repository.update_contract(contract)
        return self.buildContractDto(contract)

    def delete_contract(self, delivery_point: str) -> None:
        """
        This service is used to delete the contract by the contract delivery point
        :param delivery_point:
        :return: None
        """
        contract: SubscriberContract = self.subscriber_contract_repository.get_contract_by_delivery_point(
            delivery_point
        )
        if contract is None:
            raise DeleteContractException
        contract.deleted_at = date.today()
        contract.is_activated = False
        contract.closing_date = date.today()

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

    def get_contract_by_contract_uid_for_client(self, contract_uid: str) -> ContractDto:
        """
        This service is used to fill activated contract by a specific contract unique number
        :param contract_uid: contract unique number
        :return: SubscriberContract or throw an HTTPException error
        """
        contract: List[SubscriberContract] = self.subscriber_contract_repository \
            .get_contract_by_contract_uid_for_client(contract_uid)
        if contract is None:
            raise ContractNotFound

        return self.buildContractDto(contract)

    def get_contact_by_opening_date_for_client(self, opening_date: date, offset: int, limit: int) \
            -> List[ContractDto]:
        """
        This service allow filtering activated contract by his opening date
        :param opening_date: contract opening date
        :param offset: start page
        :param limit: end page
        :return: List of contract between offset and limit
        """
        contract: List[SubscriberContract] = self.subscriber_contract_repository \
            .get_contact_by_opening_date_for_client(opening_date, offset, limit)
        if len(contract) == 0:
            raise ContractNotFound
        return [self.buildContractDto(c) for c in contract]

    def get_contract_by_contract_uid_for_microservice_billing(self, contract_uid: str) \
            -> ContractDtoForBillingMicroService:
        contract: SubscriberContract = self.subscriber_contract_repository.get_contract_by_contract_uid_for_client(
            contract_uid
        )
        if contract is None:
            raise ContractNotFound
        # If is_bocked_payment equal to True, that mean that we don't need de request a
        # ref service for getting a pricing, dunning for the contract, so all calculation should be doing
        # according to the pricing and dunning providing by this microservice.
        # If not we have to get the pricing and dunning from the reference microservice
        if contract.infos['is_bocked_payment']:
            return ContractDtoForBillingMicroService(
                subscriber_type=contract.infos['subscription_type'],
                power_of_energy=contract.infos['power_of_energy'],
                status=contract.infos['status'],
                invoicing_frequency=contract.infos['invoicing_frequency'],
                delivery_point=contract.infos['delivery_point'],
                metric_number=contract.infos['metric_number'],
                level=contract.infos['level'],
                pricing=contract.infos['pricing'],
                dunning=contract.infos['dunning'],
                tracking_type=contract.infos['tracking_type']
            )
        # Request to the reference microservice
        else:
            return None

    def get_contact_by_closing_date_for_client(self, closing_date: date, offset: int, limit: int) \
            -> List[ContractDto]:
        """
        This service allow filtering activated contract by his opening date
        :param closing_date: contract opening date
        :param offset: start page
        :param limit: end page
        :return: List of contract between offset and limit
        """
        contract: List[SubscriberContract] = self.subscriber_contract_repository \
            .get_contact_by_opening_date_for_client(closing_date, offset, limit)
        if len(contract) == 0:
            raise ContractNotFound
        return [self.buildContractDto(c) for c in contract]

    def get_contract_by_contact_uid_and_contract_uid_for_client(self, contract_uid: str, contact_uid: str) \
            -> ContractDto:
        """
        This service is used to filter activated contracts for a specific contact by his contact number
        :param contract_uid: unique contract's number
        :param contact_uid: unique contact's number
        :return: Contract or throw an HTTPException 404
        """
        contract: SubscriberContract = self.subscriber_contract_repository \
            .get_contract_by_contact_uid_and_contract_uid_for_client(contract_uid, contact_uid)
        if contract is None:
            raise ContractNotFound
        return self.buildContractDto(contract)

    def get_contract_by_contact_pid_and_contract_uid_for_client(self, contract_uid: str,
                                                                contact_pid: str) -> List[ContractDto]:
        """
        This service filter the activated contracts for a specific contact pid
        (personal identity number of contact is can be passport number or ID number)
        :param contract_uid:
        :param contact_pid:
        :return:
        """
        contract: List[SubscriberContract] = self.subscriber_contract_repository \
            .get_contract_by_contact_pid_and_contract_uid_for_client(contract_uid, contact_pid)
        if contract is None:
            raise ContractNotFound
        return self.buildContractDto(contract)

    def get_contract_by_status_for_client(self, status: str, offset: int, limit: int) -> List[ContractDto]:
        """
        This service filter the activated contract by the given status
        :param status: contract's status
        :param offset: start pagination
        :param limit: end of pagination
        :return: List of SubscriberContract or throw an HTTPException 404
        """
        contract: List[SubscriberContract] = self.subscriber_contract_repository \
            .get_contract_by_status_for_client(status, offset, limit)
        if len(contract) == 0:
            raise ContractNotFound
        return [self.buildContractDto(c) for c in contract]

    def get_contract_by_contract_id_and_order_by_opening_date_for_client(self, contact_id: int, offset: int, limit: int) \
            -> List[ContractDto]:
        """
        This service filter activated contract by contact id and sort by opening date
        :param contact_id: contact id from db
        :param offset: start pagination
        :param limit: end of pagination
        :return: List SubscriberContract
        """
        contract: List[SubscriberContract] = self.subscriber_contract_repository \
            .get_contract_by_contract_id_and_order_by_opening_date_for_client(contact_id, offset, limit)
        if len(contract) == 0:
            raise ContractNotFound
        return [self.buildContractDto(c) for c in contract]

    def get_contract_where_opening_date_between_two_dates_for_client(self, start_date: date, end_date: date,
                                                                     offset: int, limit: int) \
            -> List[ContractDto]:
        """
        This service filter contracts where the opening date is between two dates
        :param start_date: start date for filter
        :param end_date: end date
        :param offset: start of pagination
        :param limit: end of pagination
        :return: List of SubscriberContract or throw an HTTPException error 404
        """
        contract: List[SubscriberContract] = self.subscriber_contract_repository \
            .get_contract_where_opening_date_between_two_dates_for_client(start_date, end_date, offset, limit)
        if len(contract) == 0:
            raise ContractNotFound
        return [self.buildContractDto(c) for c in contract]

    def get_contract_where_opening_date_before_given_date_for_client(self, given_date: date,
                                                                     offset: int, limit: int) \
            -> List[ContractDto]:
        """
        This service filter contracts before given_date and order
        by opening date
        :param given_date: given date for filter
        :param offset: start of pagination
        :param limit: end of pagination
        :return: List of SubscriberContract
        """
        contract: List[SubscriberContract] = self.subscriber_contract_repository \
            .get_contract_where_opening_date_before_given_date_for_client(given_date, offset, limit)
        if len(contract) == 0:
            raise ContractNotFound
        return [self.buildContractDto(c) for c in contract]

    def get_contract_where_opening_date_after_given_date_for_client(self, given_date: date, offset: int, limit: int) \
            -> List[ContractDto]:
        """
        This service filter contracts after given_date and order
        by opening date
        :param given_date: start date for filter
        :param offset: start of pagination
        :param limit: end of pagination
        :return: List of Contract or throw an HTTPException 404
        """
        contract: List[SubscriberContract] = self.subscriber_contract_repository \
            .get_contract_where_opening_date_after_given_date_for_client(given_date, offset, limit)
        if len(contract) == 0:
            raise ContractNotFound
        return [self.buildContractDto(c) for c in contract]

    def get_contract_where_opening_date_equal_given_date_for_client(self, given_date: date, offset: int, limit: int) \
            -> List[ContractDto]:
        """
        This service filter the activated contract where the opening date is equal to the providing given_date and order
        by opening date
        :param given_date: given date to compare
        :param offset: start of pagination
        :param limit: end of pagination
        :return: List Contract or throw an HTTPException 404
        """
        contract: List[SubscriberContract] = self.subscriber_contract_repository \
            .get_contract_where_opening_date_equal_given_date_for_client(given_date, offset, limit)
        if len(contract) == 0:
            raise ContractNotFound
        return [self.buildContractDto(c) for c in contract]

    def get_contract_where_closing_date_before_given_date_for_client(self, given_date: date, offset: int, limit: int) \
            -> List[ContractDto]:
        """
        This service filter activated contract where the closing is before the providing given_date and order
        by closing date
        :param given_date: given date to compare
        :param offset: start of pagination
        :param limit: end of pagination
        :return: List Contract or throw an HTTPException 404
        """
        contract: List[SubscriberContract] = self.subscriber_contract_repository \
            .get_contract_where_closing_date_before_given_date_for_client(
            given_date,
            offset,
            limit
        )
        if len(contract) == 0:
            raise ContractNotFound
        return [self.buildContractDto(c) for c in contract]

    def get_contract_where_closing_date_after_given_date_for_client(self, given_date: date, offset: int, limit: int) \
            -> List[ContractDto]:
        contract: List[SubscriberContract] = self.subscriber_contract_repository \
            .get_contract_where_closing_date_after_given_date_for_client(
            given_date,
            offset,
            limit
        )
        if len(contract) == 0:
            raise ContractNotFound

        return [self.buildContractDto(c) for c in contract]

    def get_contract_where_closing_date_equal_given_date_for_client(self, given_date: date, offset: int, limit: int) \
            -> List[ContractDto]:
        """
        This service filter activated contracts where the closing date is equal to the providing given_date and order
        by closing date
        :param given_date: given date to compare
        :param offset: start of pagination
        :param limit: end of pagination
        :return: List SubscriberContract or throw an HTTPException 404
        """
        contract: List[SubscriberContract] = self.subscriber_contract_repository \
            .get_contract_where_closing_date_equal_given_date_for_client(
            given_date,
            offset,
            limit
        )
        if len(contract) == 0:
            raise ContractNotFound
        return [self.buildContractDto(c) for c in contract]

    def get_contract_by_delivery_point_and_contact_uid_for_client(self, delivery_point: int, contact_uid: str) \
            -> ContractDto:
        """
        This function filter an activated contract by the delivery point address and contact uid
        :param delivery_point: unique address of delivery point
        :param contact_uid: this is a unique contact number
        :return: return an optional of SubscriberContract
        """
        contract: Optional[SubscriberContract] = self.subscriber_contract_repository \
            .get_contract_by_delivery_point_and_contact_uid_for_client(
            delivery_point,
            contact_uid
        )
        if contract is None:
            raise ContractNotFound
        return self.buildContractDto(contract)

    def get_contract_by_delivery_point(self, delivery_point: str) -> ContractDto:
        """
        This function filter an activated contract by the delivery point
        :param delivery_point:  unique address of delivery point
        :return: SubscriberContract
        """
        contract: SubscriberContract = self.subscriber_contract_repository \
            .get_contract_by_delivery_point(delivery_point)
        if contract is None:
            raise ContractNotFound
        return self.buildContractDto(contract)

    def get_contract_by_submitted_params(self,
                                         params: ContractDtoIncoming,
                                         infos: SubscriberContractInfoForFilter,
                                         agency: AgencyIncomingFilter,
                                         offset: int,
                                         limit: int,

                                         ) \
            -> List[ContractDto]:
        """
        This function fileter a contract by submitted params
        :param previous_level:
        :param level:
        :param agency:
        :param infos:
        :param limit:
        :param offset:
        :param params:
        :return:
        """
        # infos = json.loads(infos.json())
        filter_params = {}
        if params.dict(exclude_none=True):
            filter_params.update(params.dict(exclude_none=True))
        print(params.dict(exclude_none=True).keys())
        print(agency.dict(exclude_none=True).keys())

        # logging.warning("excluded id", params.dict(exclude_none=True).)

        contract: List[SubscriberContract] = self.subscriber_contract_repository.\
            get_contract_by_submitted_params(
            params,
            infos,
            agency,
            offset,
            limit
        )
        if len(contract) == 0:
            raise ContractNotFound
        return [self.buildContractDto(c) for c in contract]
