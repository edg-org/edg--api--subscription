from datetime import date
from typing import List, Optional

from fastapi import HTTPException, status, Depends

from api.contact.models.SubscriberContractModel import SubscriberContract
from api.contact.services.ContactsService import ContactsService
from subscriber_api.exceptions import ContractNotFound
from subscriber_api.repositories.SubscriberContractRepository import SubscriberContractRepository
from subscriber_api.schemas.SubscriberContractSchema import ContractDto


class InvestigateSubscriberContractService:
    subscriber_contract_repository: SubscriberContractRepository
    contact_service: ContactsService
    contractDto: ContractDto

    def __init__(self,
                 subscriber_contract: SubscriberContractRepository = Depends(),
                 contact_service: ContactsService = Depends(),
                 contractDto: ContractDto = Depends()
                 ) -> None:
        self.subscriber_contract = subscriber_contract
        self.contact_service = contact_service
        self.contractDto = contractDto

    def get_contract_by_customer_id_for_admin(self, costume_id: int, offset: int, limit: int) \
            -> List[ContractDto]:
        """
        This service is used  to filter activated contract by costumer id
        :param costume_id: costumer id
        :param offset: start page
        :param limit: end page
        :return: throw an error the contract does not exist or return SubscriberContract
         """
        contract: SubscriberContract = self.subscriber_contract_repository \
            .get_contract_by_customer_id_for_admin(costume_id, offset, limit)
        if contract is None:
            raise ContractNotFound
        return self.contractDto.normalize(contract)

    def get_contract_by_contract_uid_for_admin(self, contract_uid: str) -> ContractDto:
        """
        This service is used to fill activated contract by a specific contract unique number
        :param contract_uid: contract unique number
        :return: SubscriberContract or throw an HTTPException error
        """
        contract: List[SubscriberContract] | None = self.subscriber_contract_repository \
            .get_contract_by_contract_uid_for_admin(contract_uid)
        if contract is None:
            raise ContractNotFound

        return self.contractDto.normalize(contract)

    def get_contact_by_opening_date_for_admin(self, opening_date: date, offset: int, limit: int) \
            -> List[ContractDto]:
        """
        This service allow filtering activated contract by his opening date
        :param opening_date: contract opening date
        :param offset: start page
        :param limit: end page
        :return: List of contract between offset and limit
        """
        contract: List[SubscriberContract] = self.subscriber_contract_repository \
            .get_contact_by_opening_date_for_admin(opening_date, offset, limit)
        if len(contract) == 0:
            raise ContractNotFound
        return [self.contractDto.normalize(c for c in contract)]

    def get_contact_by_closing_date_for_admin(self, closing_date: date, offset: int, limit: int) \
            -> List[ContractDto]:
        """
        This service allow filtering activated contract by his opening date
        :param closing_date: contract opening date
        :param offset: start page
        :param limit: end page
        :return: List of contract between offset and limit
        """
        contract: List[SubscriberContract] = self.subscriber_contract_repository \
            .get_contact_by_opening_date_for_admin(closing_date, offset, limit)
        if len(contract) == 0:
            raise ContractNotFound
        return [self.contractDto.normalize(c for c in contract)]

    def get_contract_by_contact_uid_and_contract_uid_for_admin(self, contract_uid: str, contact_uid: str) \
            -> ContractDto:
        """
        This service is used to filter activated contracts for a specific contact by his contact number
        :param contract_uid: unique contract's number
        :param contact_uid: unique contact's number
        :return: Contract or throw an HTTPException 404
        """
        contract: SubscriberContract = self.subscriber_contract_repository \
            .get_contract_by_contact_uid_and_contract_uid_for_admin(contract_uid, contact_uid)
        if contract is None:
            raise ContractNotFound
        return self.contractDto.normalize(contract)

    def get_contract_by_contact_pid_and_contract_uid_for_admin(self, contract_uid: str,
                                                               contact_pid: str) -> ContractDto:
        """
        This service filter the activated contracts for a specific contact pid
        (personal identity number of contact is can be passport number or ID number)
        :param contract_uid:
        :param contact_pid:
        :return:
        """
        contract: List[SubscriberContract] = self.subscriber_contract_repository \
            .get_contract_by_contact_pid_and_contract_uid_for_admin(contract_uid, contact_pid)
        if contract is None:
            raise ContractNotFound
        return self.contractDto.normalize(contract)

    def get_contract_by_status_for_admin(self, status: str, offset: int, limit: int) -> List[ContractDto]:
        """
        This service filter the activated contract by the given status
        :param status: contract's status
        :param offset: start pagination
        :param limit: end of pagination
        :return: List of SubscriberContract or throw an HTTPException 404
        """
        contract: List[SubscriberContract] = self.subscriber_contract_repository \
            .get_contract_by_status_for_admin(status, offset, limit)
        if len(contract) == 0:
            raise ContractNotFound
        return [self.contractDto.normalize(c for c in contract)]

    def get_contract_by_contract_id_and_order_by_opening_date_for_admin(self, contact_id: int, offset: int, limit: int) \
            -> List[ContractDto]:
        """
        This service filter activated contract by contact id and sort by opening date
        :param contact_id: contact id from db
        :param offset: start pagination
        :param limit: end of pagination
        :return: List SubscriberContract
        """
        contract: List[SubscriberContract] = self.subscriber_contract_repository \
            .get_contract_by_contract_id_and_order_by_opening_date_for_admin(contact_id, offset, limit)
        if len(contract) == 0:
            raise ContractNotFound
        return [self.contractDto.normalize(c for c in contract)]

    def get_contract_where_opening_date_between_two_dates_for_admin(self, start_date: date, end_date: date,
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
            .get_contract_where_opening_date_between_two_dates_for_admin(start_date, end_date, offset, limit)
        if len(contract) == 0:
            raise ContractNotFound
        return [self.contractDto.normalize(c for c in contract)]

    def get_contract_where_opening_date_before_given_date_for_admin(self, given_date: date,
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
            .get_contract_where_opening_date_before_given_date_for_admin(given_date, offset, limit)
        if len(contract) == 0:
            raise ContractNotFound
        return [self.contractDto.normalize(c for c in contract)]

    def get_contract_where_opening_date_after_given_date_for_admin(self, given_date: date, offset: int, limit: int) \
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
            .get_contract_where_opening_date_after_given_date_for_admin(given_date, offset, limit)
        if len(contract) == 0:
            raise ContractNotFound
        return [self.contractDto.normalize(c for c in contract)]

    def get_contract_where_opening_date_equal_given_date_for_admin(self, given_date: date, offset: int, limit: int) \
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
            .get_contract_where_opening_date_equal_given_date_for_admin(given_date, offset, limit)
        if len(contract) == 0:
            raise ContractNotFound
        return [self.contractDto.normalize(c for c in contract)]

    def get_contract_where_closing_date_before_given_date_for_admin(self, given_date: date, offset: int, limit: int) \
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
            .get_contract_where_closing_date_before_given_date_for_admin(
            given_date,
            offset,
            limit
        )
        if len(contract) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="We didn't find any contract corresponding to the closing date " + str(given_date)
            )
        return [self.contractDto.normalize(c for c in contract)]

    def get_contract_where_closing_date_after_given_date_for_admin(self, given_date: date, offset: int, limit: int) \
            -> List[ContractDto]:
        contract: List[SubscriberContract] = self.subscriber_contract_repository \
            .get_contract_where_closing_date_after_given_date_for_admin(
            given_date,
            offset,
            limit
        )
        if len(contract) == 0:
            raise ContractNotFound

        return [self.contractDto.normalize(c for c in contract)]

    def get_contract_where_closing_date_equal_given_date_for_admin(self, given_date: date, offset: int, limit: int) \
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
            .get_contract_where_closing_date_equal_given_date_for_admin(
            given_date,
            offset,
            limit
        )
        if len(contract) == 0:
            raise ContractNotFound
        return [self.contractDto.normalize(c for c in contract)]

    def get_contract_by_delivery_point_and_contact_uid_for_admin(self, delivery_point: int, contact_uid: str) \
            -> Optional[ContractDto]:
        """
        This function filter an activated contract by the delivery point address and contact uid
        :param delivery_point: unique address of delivery point
        :param contact_uid: this is a unique contact number
        :return: return an optional of SubscriberContract
        """
        contract: Optional[SubscriberContract] = self.subscriber_contract_repository \
            .get_contract_by_delivery_point_and_contact_uid_for_admin(
            delivery_point,
            contact_uid
        )
        if contract is None:
            raise ContractNotFound
        return self.contractDto.normalize(contract)

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
        return self.contractDto.normalize(contract)
