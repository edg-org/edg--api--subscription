import json
import logging
from datetime import datetime
from typing import List, Sequence, cast

from fastapi import Depends
from fastapi.encoders import jsonable_encoder

from api.contact.models.SubscriberContractModel import SubscriberContract
from api.contact.schemas.pydantic.ContactsSchema import ContactOutputDto

from api.contact.services.ContactsService import ContactsService
from api.subscription.exceptions import ContractNotFound, DeleteContractException, ContactNotFound, \
    EditContactWhileNotOwner, ContractDisabled, ContractExist, ContractStatusError, RepeatingDeliveryPoint, \
    ContractLevelError, StatusErrorWhenCurrentStatusIsEqualInitial, \
    StatusErrorWhenCurrentStatusIsEqualEdited, ContractIsAlreadyActivated

from api.subscription.repositories.SubscriberContractRepository import SubscriberContractRepository
from api.subscription.schemas.SubscriberContractSchema import SubscriberContractSchema, ContractDtoIncoming, \
    ContractDto, ContractDtoWithPagination, BillingDto, SubscriberContractInfoInputUpdate, ContractDetails, \
    InvoiceDetails, ContractInvoiceDetails, ContactContracts, ContractInvoiceParams, Invoice, \
    SubscriberContractInfoOutput, ContractInvoiceForBillingService, ContactDtoForBillingService, \
    ContactWithContractAndPricing
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
            opening_date=contract.opening_date,
            closing_date=contract.closing_date,
            created_at=contract.created_at,
            updated_at=contract.updated_at,
            deleted_at=contract.deleted_at,
            is_activated=contract.is_activated,
            contract_number=contract.contract_number,
            customer_number=contract.customer_number
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
        contracts = self.subscriber_contract_repository.create_contract(contracts)
        return [self.buildContractDto(c) for c in contracts]

    def check_save_business_logic(self, contract_schema: SubscriberContractSchema) -> SubscriberContract:
        """
        This service verify if the contact and contract is already exist and the contract is not assign to any
        delivery point
        :param contract_schema:
        :return: SubscriberContract
        """
        # contract_schema.infos = json.loads(contract_schema.infos.json())
        # logging.warning(f"type of contract schema %s", type(contract_schema))
        contact: ContactOutputDto = self.contact_service.get_contact_by_uid_for_client(
            contract_schema['customer_number']
        )

        contract_exist = self.subscriber_contract_repository \
            .get_contract_by_delivery_point_on_number(
            contract_schema['delivery_point']['number']
        )

        if contract_exist is not None:
            raise ContractExist(" number " + contract_exist.infos['delivery_point']['number'])

        if contract_schema['status'] == contract_schema['previous_status']:
            raise ContractStatusError

        if contract_schema['level']['name'] == contract_schema['previous_level']:
            raise ContractLevelError

        contact = jsonable_encoder(contact)

        return SubscriberContract(
            infos=contract_schema,
            customer_id=contact['id'],
            customer_number=contract_schema['customer_number'],
            contract_number=GuidGenerator.contractUID(contact['infos']['identity']['pid']),
        )

    def update_contract(self, contract_number: str, contract_schema: SubscriberContractInfoInputUpdate) -> ContractDto:
        """
        This service update an existing contract from the database
        :param contract_number: contract unique number
        :param contract_schema: request body, the data model from db
        :return: return an updated contract's information associated to delivery point and customer_id
        """
        contract_schema = jsonable_encoder(contract_schema)
        # logging.error(contract_schema['status'])
        # Previous status should be different to current status
        if contract_schema['status'] == contract_schema['previous_status']:
            raise ContractStatusError

        contract_exist: SubscriberContract = self.subscriber_contract_repository \
            .get_contract_by_contract_uid(contract_number)
        # logging.error("update find %s", contract_exist.normalize())
        # if the contract does not exist, so we throw an exception
        if contract_exist is None:
            raise ContractNotFound

        # raise ContractDisabled
        # If the closing date is set that mean that the contract is resigned
        if contract_exist.closing_date is not None:
            raise ContractDisabled

        # check status logic
        contract_exist = self.contract_status_logic(contract_exist, contract_schema['status'])

        # Subscription type and delivery point is immutable
        # To edit the subscription type you should close the current contract and open another
        contract_schema['previous_status'] = contract_exist.infos['status']
        contract_schema['subscription_type'] = contract_exist.infos['subscription_type']
        contract_schema['delivery_point']['number'] = contract_exist.infos['delivery_point']['number']

        contract: SubscriberContract = self.subscriber_contract_repository.update_contract(
            SubscriberContract(
                id=contract_exist.id,
                infos=contract_schema,
                customer_id=contract_exist.customer_id,
                customer_number=contract_exist.customer_number,
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
        if contract.is_activated:
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

        if status == ContractStatus.ACTIVE:
            contract.opening_date = datetime.now().replace(microsecond=0)
            contract.is_activated = True

        return contract

    def delete_contract(self, contract_number: str) -> ContractDto:
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
        contract.deleted_at = datetime.now().replace(microsecond=0)
        contract.is_activated = False
        contract.closing_date = datetime.now().replace(microsecond=0)
        contract.infos = jsonable_encoder(contract.infos)
        contract.infos['status'] = ContractStatus.CLOSED
        contract: SubscriberContract = self.subscriber_contract_repository.update_contract(contract)
        return self.buildContractDto(contract)

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

        contracts: Sequence[List[SubscriberContract]] = self.subscriber_contract_repository. \
            get_contract_by_submitted_params(params, offset, limit)
        contracts: List[ContractDto] = [self.buildContractDto(c) for c in contracts]
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

    def get_pricing(self, number) -> BillingDto | None:
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
            get_billing_info([""], "http://localhost:8082/pricing", "")

    def get_contract_details(self, number, params: ContractInvoiceParams) -> List[ContractInvoiceDetails]:
        contracts: Sequence[List[SubscriberContract]] = self.subscriber_contract_repository. \
            get_contact_contracts(number, params)
        if contracts is None:
            raise ContractNotFound
        # build contract dto
        contracts: List[ContractDto] = [self.buildContractDto(c) for c in contracts]

        # get invoice from billing microservice
        if params.contract_number is not None:
            invoice: List[InvoiceDetails] = RequestMaster. \
                get_invoice(ContractInvoiceForBillingService(
                invoice_date=params.invoice_date,
                contract_number=[params.contract_number]),
                "http://localhost:8082/billing/invoice",
                "token")

        else:
            invoice: List[InvoiceDetails] = RequestMaster.get_invoice(
                ContractInvoiceForBillingService(
                    invoice_date=params.invoice_date,
                    contract_number=[c.contract_number for c in contracts]
                ),
                "http://localhost:8082/billing/invoice",
                "")

        return [self.buildContractInvoiceDetails(i.invoice, c) for i in invoice for c in contracts]

    def buildContractInvoiceDetails(self, invoice: List[Invoice], contract: ContractDto) \
            -> ContractInvoiceDetails:
        return ContractInvoiceDetails(
            consumption_estimated=contract.infos.consumption_estimated,
            subscription_type=contract.infos.subscription_type,
            payment_deadline=contract.infos.payment_deadline,
            deadline_unit_time=contract.infos.deadline_unit_time,
            subscribed_power=contract.infos.subscribed_power,
            power_of_energy=contract.infos.power_of_energy,
            status=contract.infos.status,
            previous_status=contract.infos.previous_status,
            level=contract.infos.level,
            previous_level=contract.infos.previous_level,
            invoicing_frequency=contract.infos.invoicing_frequency,
            delivery_point=contract.infos.delivery_point,
            agency=contract.infos.agency,
            home_infos=contract.infos.home_infos,
            is_bocked_payment=contract.infos.is_bocked_payment,
            pricing=contract.infos.pricing,
            dunning=contract.infos.dunning,
            tracking_type=contract.infos.tracking_type,
            invoice=invoice
        )

    def get_contract_and_contact_by_contract_uid(self, number: List[str]) -> ContactWithContractAndPricing:
        contracts: List[SubscriberContract] = []
        subscriber_type: List[str] = []
        for contract_number in number:
            contract = self.subscriber_contract_repository.get_contract_by_contract_uid(contract_number)
            if contract is not None:
                if contract.infos['subscription_type']['name'] not in subscriber_type:
                    subscriber_type.append(contract.infos['subscription_type']['name'])
                contracts.append(contract)
        try:
            pricing: List[BillingDto] = RequestMaster.get_billing_info(subscriber_type, "http://localhost:8082/pricing", "")
        except:
            pricing = [BillingDto()]
        # logging.error(f"aaaa %s ", contracts[0].contacts.infos)
        contracts: List[ContactDtoForBillingService] = [ContactDtoForBillingService(
            contact=c.contacts.infos,
            id=c.id,
            infos=c.infos,
            opening_date=c.opening_date,
            closing_date=c.closing_date,
            created_at=c.created_at,
            updated_at=c.updated_at,
            deleted_at=c.deleted_at,
            is_activated=c.is_activated,
            contract_number=c.contract_number,
            customer_number=c.customer_number
        ) for c in contracts]

        return ContactWithContractAndPricing(
            contact_contract=contracts,
            subscriber_type_pricing_infos=pricing
        )
