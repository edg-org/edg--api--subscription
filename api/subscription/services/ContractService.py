import json
from fastapi import Depends
from typing import List, Sequence, cast, Any
from datetime import datetime, timedelta, date
from fastapi.encoders import jsonable_encoder

from api.configs.Database import env
from api.subscription.utilis.Status import ContractStatus
from api.subscription.models.ContractModel import Contract
from api.subscription.services.GuidGenerator import GuidGenerator
from api.subscription.services.RequestMaster import RequestMaster
from api.subscriber.schemas.ContactsSchema import ContactOutputDto
from api.subscriber.services.ContactsService import ContactsService
from api.subscription.repositories.ContractRepository import ContractRepository
from api.subscription.exceptions import (
    ContractNotFound,
    DeleteContractException,
    ContractDisabled,
    ContractExist,
    ContractStatusError,
    RepeatingDeliveryPoint,
    ContractLevelError,
    StatusErrorWhenCurrentStatusIsEqualInitial,
    StatusErrorWhenCurrentStatusIsEqualEdited,
    ContractIsAlreadyActivated,
    ContactOrContractNotFound, RequestResourceError
)
from api.subscription.schemas.ContractSchema import (
    ContractSchema,
    ContractDto,
    ContractDtoWithPagination,
    ContractInfoInputUpdate,
    InvoiceDetails,
    ContractInvoiceDetails,
    ContractInvoiceParams,
    Invoice,
    ContractInvoiceForBillingService,
    ContactDtoForBillingService,
    ContactWithContractAndPricing,
    ContractDtoQueryParams, PricingDto, Pricing
)


class ContractService:
    contract_repository: ContractRepository
    contact_service: ContactsService

    def __init__(self,
                 contract_repository: ContractRepository = Depends(),
                 contact_service: ContactsService = Depends()
                 ) -> None:
        self.contract_repository = contract_repository
        self.contact_service = contact_service

    def buildContractDto(self, contract: Contract) -> ContractDto:
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

    async def create_contract(self, contract_schema: List[ContractSchema], token: str) -> List[ContractDto]:
        """
        This service has a purpose to create a new contract
        :param token:
        :param contract_schema: the data model to fill
        :return: return a created object from db Contract
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
            if not contract['is_blocked_pricing']:
                contract['pricing'] = None
                contract['dunning'] = None
        if (len(delivery_points_on_number) != len(contract_schema) or
                len(delivery_point_on_metric_number) != len(contract_schema)):
            raise RepeatingDeliveryPoint

        contracts: List[Contract] = [await self.check_save_business_logic(c, token) for c in contract_schema]
        contracts = self.contract_repository.create_contract(contracts)
        return [self.buildContractDto(c) for c in contracts]

    async def check_save_business_logic(self, contract_schema: ContractSchema, token: str) -> Contract:
        """
        This service verify if the contact and contract is already exist and the contract is not assign to any
        delivery point
        :param token:
        :param contract_schema:
        :return: Contract
        """
        # contract_schema.infos = json.loads(contract_schema.infos.json())
        # logging.warning(f"type of contract schema %s", type(contract_schema))
        contact: ContactOutputDto = self.contact_service.get_contact_by_uid_for_client(
            contract_schema['customer_number']
        )

        contract_exist = self.contract_repository \
            .get_contract_by_delivery_point_on_number(
            contract_schema['delivery_point']['number']
        )

        if contract_exist is not None:
            raise ContractExist(" number " + contract_exist.infos['delivery_point']['number'])

        contract_exist = self.contract_repository.get_contract_by_delivery_point_on_metric_number(
            contract_schema['delivery_point']['metric_number']
        )

        if contract_exist is not None:
            raise ContractExist(" metric number " + contract_exist.infos['delivery_point']['metric_number'])

        if contract_schema['status'] == contract_schema['previous_status']:
            raise ContractStatusError

        if contract_schema['level']['name'] == contract_schema['previous_level']:
            raise ContractLevelError

        # for each contract we have to get the pricing information from referential service if is_bocked_pricing is true
        contract_schema['pricing'] = jsonable_encoder(await self.get_pricing(contract_schema['is_blocked_pricing'],
                                                                       contract_schema['subscription_type']['code'], token))
        contact = jsonable_encoder(contact)

        return Contract(
            infos=contract_schema,
            customer_id=contact['id'],
            customer_number=contract_schema['customer_number'],
            contract_number=GuidGenerator.contractUID(contact['infos']['identity']['pid']),
        )

    async def get_pricing(self, is_bocked_pricing: bool, subscription_code: str, token: str) -> Pricing:
        if is_bocked_pricing:
            try:
                pricing = json.loads(await RequestMaster.get_pricing_info(
                    f"{env.referential_domain_name}/api/v1/subscriptiontypes/" + subscription_code,
                    token
                ))
                print("=======================>>Correct pricing ============> ", pricing['pricing'])
                return pricing['pricing']
            except:
                raise RequestResourceError

    def update_contract(self, contract_number: str, contract_schema: ContractInfoInputUpdate) -> ContractDto:
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

        contract_exist: Contract = self.contract_repository \
            .get_contract_by_contract_uid(contract_number)
        # logging.error("update find %s", contract_exist.normalize())
        # if the contract does not exist, so we throw an exception
        if contract_exist is None:
            raise ContractNotFound

        # raise ContractDisabled
        # If the closing date is set that mean that the contract is resigned
        if contract_exist.closing_date is not None:
            raise ContractDisabled

        # check if delivery point on metric_number exist, if true throw error
        contract_exist_by_delivery_point_on_metric_number = self.contract_repository.get_contract_by_delivery_point_on_metric_number(
            contract_schema['delivery_point']['metric_number'])
        # logging.error("metric number %s", contract_exist_by_delivery_point_on_metric_number)
        if (contract_exist_by_delivery_point_on_metric_number is not None
                and contract_exist_by_delivery_point_on_metric_number.contract_number != contract_exist.contract_number
        ):
            raise ContractExist(" metric number " + contract_schema['delivery_point']['metric_number'] +
                                " Please provide a correct metric number")

        # check status logic
        contract_exist = self.contract_status_logic(contract_exist, contract_schema['status'])

        # Subscription type and delivery point is immutable
        # To edit the subscription type you should close the current contract and open another
        contract_schema['previous_status'] = contract_exist.infos['status']
        contract_schema['subscription_type'] = contract_exist.infos['subscription_type']
        contract_schema['delivery_point']['number'] = contract_exist.infos['delivery_point']['number']
        # check if is_blocked_pricing is set
        if contract_schema['is_blocked_pricing']:
            # we have to fetch pricing info from referential service
            contract_schema['pricing'] = jsonable_encoder(self.get_pricing(contract_schema['is_blocked_pricing'],
                                                                           contract_schema['subscription_type'][
                                                                               'code']))

        # if the flag is set to false, so the pricing is None
        if not contract_schema['is_blocked_pricing']:
            contract_schema['pricing'] = None
        # set immutables fields
        contract_schema['payment_deadline'] = contract_exist.infos['payment_deadline']
        contract_schema['deadline_unit_time'] = contract_exist.infos['deadline_unit_time']
        contract_schema['subscribed_power'] = contract_exist.infos['subscribed_power']
        contract_schema['power_of_energy'] = contract_exist.infos['power_of_energy']
        contract_schema['agency'] = contract_exist.infos['agency']

        contract: Contract = self.contract_repository.update_contract(
            Contract(
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
        contract: Contract = self.contract_repository.get_contract_by_contract_uid_for_update(contract_number)
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
        contract = self.contract_repository.update_contract(contract)

        return self.buildContractDto(contract)

    def contract_status_logic(self, contract: Contract, status: str) -> Contract:
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
        contract: Contract = self.contract_repository.get_contract_by_contract_uid(contract_number)
        if contract is None:
            raise DeleteContractException
        contract.deleted_at = datetime.now().replace(microsecond=0)
        contract.is_activated = False
        contract.closing_date = datetime.now().replace(microsecond=0)
        contract.infos = jsonable_encoder(contract.infos)
        contract.infos['status'] = ContractStatus.CLOSED
        contract: Contract = self.contract_repository.update_contract(contract)
        return self.buildContractDto(contract)

    def get_contract_by_customer_id_for_client(self, customer_id: int, offset: int, limit: int) -> List[ContractDto]:
        """
        This service is used  to filter activated contract by costumer id
        :param customer_id:
        :param offset: start page
        :param limit: end page
        :return: throw an error the contract does not exist or return Contract
         """
        contract: List[Contract] = self.contract_repository \
            .get_contract_by_customer_id_for_client(customer_id, offset, limit)

        if len(contract) == 0:
            raise ContractNotFound

        return [self.buildContractDto(c) for c in contract]

    def get_contract_by_contract_uid(self, contract_number: str) -> ContractDto:
        """
        This service is used to fill activated contract by a specific contract unique number
        :param contract_number: contract unique number
        :return: Contract or throw an HTTPException error
        """
        contract: Contract = self.contract_repository \
            .get_contract_by_contract_uid(contract_number)
        if contract is None:
            raise ContractNotFound

        return self.buildContractDto(contract)

    def get_contract_by_submitted_params(self, params: ContractDtoQueryParams, offset: int,
                                         limit: int) -> ContractDtoWithPagination:
        """
        This function fileter a contract by submitted params
        :param offset:
        :param limit:
        :param params:
        :return:
        """
        # logging.warning("excluded id", params.dict(exclude_none=True).)

        contracts: Sequence[List[Contract]] = self.contract_repository.get_contract_by_submitted_params(params, offset,
                                                                                                        limit)
        contracts: List[ContractDto] = [self.buildContractDto(c) for c in contracts]
        if len(contracts) == 0:
            raise ContractNotFound
        return self.buildContractDtoWithPagination(contracts, offset, limit,
                                                   self.contract_repository.count_contract(params))

    def get_contract_by_contact_number(self, contact_number: str, offset: int, limit: int) -> ContractDtoWithPagination:
        """
        This method get contract information by contact number
        :param contact_number:
        :param offset:
        :param limit:
        :return: ContractDtoWithPagination
        """
        contracts = self.contract_repository.get_contract_by_contact_number(contact_number)
        if len(contracts) == 0:
            raise ContractNotFound
        contracts = [self.buildContractDto(c) for c in contracts]
        return self.buildContractDtoWithPagination(
            contracts, offset, limit, self.contract_repository.
            count_contract_by_contact_number(contact_number)
        )

    def get_contracts_by_contact_number(self, contact_number) -> List[ContractDto]:
        """
        Return all contract by customer number
        :param contact_number:
        :return:  List[ContractDto] or empty List
        """
        contracts = self.contract_repository.get_contract_by_contact_number(contact_number)
        if len(contracts) == 0:
            raise ContractNotFound
        return [self.buildContractDto(c) for c in contracts]

    def get_contract_details(self, number, params: ContractInvoiceParams) -> List[ContractInvoiceDetails]:
        contracts: Sequence[List[Contract]] = self.contract_repository. \
            get_contact_contracts(number, params)
        if len(contracts) == 0:
            raise ContactOrContractNotFound
        # build contract dto
        contracts: List[ContractDto] = [self.buildContractDto(c) for c in contracts]
        print("=======================> contract =========>", jsonable_encoder(contracts))

        """
           Managing of invoice_date_start and invoice_date_end
            --- if invoice_date_start is empty and invoice_date_end is too, so we take the current month-1 for 
            the invoice_date_start and current month -6 for the invoice_date_end
            --- if invoice_date_start is not empty and invoice_date_end is empty, so we initialize the invoice_date_end 
            to invoice_date_start
            --- if invoice_date_start is not empty and invoice_date_start is not empty, we will check the interval 
            between those date, if the interval is more than 6 month, so we will return the last resent 6 months 
            according to the current month.
            The invoice_date_start and invoice_date_end starts and the first day of month
        """
        if params.invoice_date_end is None and params.invoice_date_start is None:
            params.invoice_date_start = (timedelta(weeks=-4) + date.today()).replace(day=1)
            params.invoice_date_end = (timedelta(weeks=-4 * 7) + date.today()).replace(day=1)

        if params.invoice_date_start is not None and params.invoice_date_end is None:
            params.invoice_date_end = params.invoice_date_start

        # If the interval of date is more than 6 months
        if (
                params.invoice_date_start is not None
                and
                params.invoice_date_end is not None
                and
                (params.invoice_date_start - params.invoice_date_end).days > 168
        ):
            params.invoice_date_end = (timedelta(weeks=-4 * 6) + params.invoice_date_start).replace(day=1)

        # logging.error("start date "+str(params.invoice_date_start) + " end date " + str(params.invoice_date_end))

        # get invoice from billing microservice
        if params.contract_number is not None:
            invoice: List[InvoiceDetails] = RequestMaster. \
                get_invoice(ContractInvoiceForBillingService(
                invoice_date_start=params.invoice_date_start,
                invoice_date_end=params.invoice_date_end,
                contract_number=[params.contract_number]),
                "http://localhost:8082/billing/invoice",
                "token")

        # else:
        #     try:
        #         invoice: List[InvoiceDetails] = RequestMaster.get_invoice(
        #             ContractInvoiceForBillingService(
        #                 invoice_date_start=params.invoice_date_start,
        #                 invoice_date_end=params.invoice_date_end,
        #                 contract_number=[c.contract_number for c in contracts]
        #             ),
        #             "http://localhost:8082/billing/invoice",
        #             "")
        #     except:
        #         return [self.buildContractInvoiceDetails(i.invoice, c) for i in [] for c in contracts]

        return [self.buildContractInvoiceDetails([], c) for c in contracts]

    def buildContractInvoiceDetails(self, invoice: List[Invoice], contract: ContractDto) -> ContractInvoiceDetails:
        return ContractInvoiceDetails(
            consumption_estimated=str(contract.infos.consumption_estimated.value) + " " +
                                  str(contract.infos.consumption_estimated.measurement_unit),
            subscription_type=contract.infos.subscription_type.name,
            payment_deadline=contract.infos.payment_deadline,
            subscribed_power=contract.infos.subscribed_power,
            delivery_point=contract.infos.delivery_point,
            agency=contract.infos.agency,
            is_bocked_pricing=contract.infos.is_blocked_pricing,
            invoice=invoice
        )

    async def get_contract_and_contact_by_contract_uid(self, number: List[str],
                                                       token: str) -> ContactWithContractAndPricing:
        contractsDto: List[Contract] = []
        for contract_number in number:
            contract = self.contract_repository.get_contract_by_contract_uid(contract_number)
            if contract is not None:
                if not contract.infos['is_blocked_pricing']:

                    try:
                        pricing = json.loads(await RequestMaster.get_pricing_info(
                            f"{env.referential_domain_name}/api/v1/subscriptiontypes/"+
                            str(contract.infos['subscription_type']['code']),
                            token
                        ))
                        contract.infos['pricing'] = pricing['pricing']

                    except Exception as e:
                        raise RequestResourceError
                contractsDto.append(contract)

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
        ) for c in contractsDto]

        return ContactWithContractAndPricing(
            contact_contract=contracts
        )
