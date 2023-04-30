from datetime import date
from typing import List, Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models.ContactsModel import Contacts
from subscriber_api.models.SubscriberContractModel import SubscriberContract
from subscriber_api.configs.Database import get_db_connection
from subscriber_api.schemas.SubscriberContractSchema import ContractDtoIncoming, SubscriberContractInfoForFilter, \
    Agency, AgencyIncomingFilter, SubscriptionLevel, SubscriptionLevelIncomingFilter, SubscriptionType


class SubscriberContractRepository:
    db: Session

    def __init__(self, db: Session = Depends(get_db_connection)) -> None:
        self.db = db

    def create_contract(self, subscriber_contract: List[SubscriberContract]) -> List[SubscriberContract]:
        """
        This function is designed to create a new subscriber's contract, it received  as
        :param subscriber_contract: is an ORM model of the table subscriber_contract that own
        all information about contract
        :return: SubscriberContract
        """
        self.db.add_all(subscriber_contract)
        self.db.commit()
        return subscriber_contract

    def update_contract(self, subscriber_contract: SubscriberContract) -> SubscriberContract:
        """
        This function is used to update user information from the SubscriberContract table
        :param subscriber_contract: is an ORM model of the table subscriber_contract that own
        all information about contract
        :return: SubscriberContract
        """
        self.db.merge(subscriber_contract)
        self.db.commit()
        return subscriber_contract

    def delete_contract(self, contract: SubscriberContract) -> None:
        """
        To resign the contract between EDG and customer use this function,
        while resigning the table SubscriberContract will be updated with the flag
        is_activated: False.
        :param costumer_id: the id of customer to delete
        :return: None
        """
        self.db.merge(contract)
        self.db.commit()

    # Filters

    def get_contract_by_customer_id_for_client(self, costumer_id: int, offset: int, limit: int) -> \
            List[SubscriberContract]:
        """
        This function fetch all contract for the given costume_id and the given pagination where the is_activated is
        equal to True
        :param costumer_id: customer id from db
        :param offset: start of pagination
        :param limit: end of pagination
        :return: List of SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract).where(
            SubscriberContract.customer_id == costumer_id,
            SubscriberContract.is_activated == False
        ).offset(offset).limit(limit)).all()

    def get_contract_by_customer_id_for_admin(self, customer_id: int, offset: int, limit: int) \
            -> List[SubscriberContract]:
        """
         This function fetch all contract for the given costume_id and the given pagination where the is_activated is
         equal to True or False
        :param costume_id: customer id from db
        :param offset: start pagination
        :param limit: end pagination
        :return: List of SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract).where(
            SubscriberContract.customer_id == customer_id
        ).offset(offset).limit(limit)).all()

    def get_contract_by_contract_uid(self, contract_uid: str) -> SubscriberContract:
        """
        This function fetch the contract information corresponding to given contract_uid
        (unique contract ID for the contract) where is_activated is equal to True
        :param contract_uid: unique contract number
        :return:SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract).where(
            SubscriberContract.contract_uid.ilike(contract_uid)
        )).first()

    def get_contract_by_contract_uid_for_admin(self, contract_uid: str) -> SubscriberContract:
        """
        This function fetch the contract information corresponding to given contract_uid
        (unique contract ID for the contract) where is_activated is equal to True or False
        :param contract_uid: unique contract number
        :return:SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract).where(
            SubscriberContract.contract_uid.ilike(contract_uid.lower())
        )).first()

    def get_contact_by_opening_date_for_client(
            self,
            opening_date: date,
            offset: int,
            limit: int
    ) -> List[SubscriberContract]:
        """
        This function fetch all activated(is_activated is equal to True) contracts according to the providing to
        the date when the contract is opened
        :param opening_date: the date when the contract is opened (format yyyy-mm-dd)
        :param offset: start pagination
        :param limit: end pagination
        :return: List of SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract).where(
            SubscriberContract.opening_date == opening_date,
            SubscriberContract.is_activated == False
        ).offset(offset).limit(limit)).all()

    def get_contact_by_opening_date_for_admin(
            self,
            opening_date: date,
            offset: int,
            limit: int
    ) -> List[SubscriberContract]:
        """
        This function  fetch all activated and not resigned contract (is_activated is equal to True or False)
        contracts according to the providing to
        the date when the contract is opened
        :param opening_date:
        :param offset:
        :param limit:
        :return: List of SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract).where(
            SubscriberContract.opening_date == opening_date
        ).offset(offset).limit(limit)).all()

    def get_contact_by_closing_date_for_client(
            self,
            closing_date: date,
            offset: int,
            limit: int
    ) -> List[SubscriberContract]:
        """
        This function fetch all activated(is_activated is equal to True) contracts according to the providing to
        the date when the contract is opened
        :param closing_date: the date when the contract is opened (format yyyy-mm-dd)
        :param offset: start pagination
        :param limit: end pagination
        :return: List of SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract).where(
            SubscriberContract.closing_date == closing_date,
            SubscriberContract.is_activated == True
        ).offset(offset).limit(limit)).all()

    def get_contact_by_closing_date_for_admin(
            self,
            closing_date: date,
            offset: int,
            limit: int
    ) -> List[SubscriberContract]:
        """
        This function  fetch all activated and not resigned contract (is_activated is equal to True or False)
        contracts according to the providing to
        the date when the contract is opened
        :param closing_date: the date when the contract is opened (format yyyy-mm-dd)
        :param offset:
        :param limit:
        :return: List of SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract).where(
            SubscriberContract.closing_date == closing_date
        ).offset(offset).limit(limit)).all()

    def get_contract_by_contact_uid_and_contract_uid_for_client(self, contract_uid: str, contact_uid: str) \
            -> SubscriberContract:
        """
        This function is used to filter activated contracts for a specific contact by his contact number
        :param contract_uid: unique contract's ID
        :param contact_uid: contact unique ID format (CL+7chifers)
        :return: SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract).join(Contacts).where(
            SubscriberContract.contract_uid.ilike(contract_uid),
            Contacts.contact_uid.ilike(contact_uid),
            SubscriberContract.is_activated == False
        )).first()

    def get_contract_by_contact_uid_and_contract_uid_for_admin(self, contract_uid: str, contact_uid: str) \
            -> SubscriberContract:
        """
        This function is used to filter contracts (activated and disabled) for a specific contact by his contact number
        :param contract_uid: unique contract's ID
        :param contact_uid: contact unique ID format (CL+7chifers)
        :return: SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract).join(Contacts).where(
            SubscriberContract.contract_uid.ilike(contract_uid),
            Contacts.contact_uid.ilike(contact_uid)
        )).first()

    def get_contract_by_contact_pid_and_contract_uid_for_client(self, contract_uid: str,
                                                                contact_pid: str) -> SubscriberContract:
        """
        This function filter the activated contracts for a specific contact pid
        (personal identity number of contact is can be passport number or ID number)
        :param contract_uid: unique contract's ID
        :param contact_pid: contact identity number (pid from Passport or ID)
        :return: SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract).join(Contacts).where(
            SubscriberContract.contract_uid.ilike(contract_uid),
            Contacts.infos['identity']['pid'] == contact_pid,
            SubscriberContract.is_activated == False
        )).first()

    def get_contract_by_contact_pid_and_contract_uid_for_admin(self, contract_uid: str,
                                                               contact_pid: str) -> SubscriberContract:
        """
        This function filter the activated contracts for a specific contact pid
        (personal identity number of contact is can be passport number or ID number)
        :param contract_uid: unique contract's ID
        :param contact_pid: contact identity number (pid from Passport or ID)
        :return: SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract).join(Contacts).where(
            SubscriberContract.contract_uid.ilike(contract_uid),
            Contacts.contact_uid.ilike(contact_pid)
        )).first()

    def get_contract_by_status_for_client(self, status: str, offset: int, limit: int) -> List[SubscriberContract]:
        """
        This function filter the activated contract by the given status
        :param status: contract's status
        :param offset: start pagination
        :param limit: end of pagination
        :return: List of SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract).where(
            SubscriberContract.infos['status'] == status,
            SubscriberContract.is_activated == True
        ).offset(offset).limit(limit)).all()

    def get_contract_by_status_for_admin(self, status: str, offset: int, limit: int) -> List[SubscriberContract]:
        """
        This function filter activated or resigned contract by the given status
        :param status:  contract's status
        :param offset: start pagination
        :param limit: end of pagination
        :return: List of SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract).where(
            SubscriberContract.infos['status'] == status
        ).offset(offset).limit(limit)).all()

    def get_deleted_contract_by_status_for_admin(self, status: str, offset: int, limit: int) -> List[
        SubscriberContract]:
        """
        This function filter resigned contract by the given status
        :param status:  contract's status
        :param offset: start pagination
        :param limit: end of pagination
        :return: List of SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract).where(
            SubscriberContract.infos['status'] == status,
            SubscriberContract.is_activated == False
        ).offset(offset).limit(limit)).all()

    def get_contract_by_contact_id_and_sort_contract_by_opening_date_for_admin(self, contact_id: int, offset: int,
                                                                               limit: int) \
            -> List[SubscriberContract]:
        """
        This function filter by contact id and sort by opening date
        :param contact_id: contact id from db
        :param offset: start pagination
        :param limit: end of pagination
        :return: List SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract)
                               .join(SubscriberContract.contacts)
                               .where(SubscriberContract.customer_id == contact_id)
                               .offset(offset)
                               .limit(limit)
                               .order_by(SubscriberContract.opening_date)
                               ).all()

    def get_contract_by_contract_id_and_order_by_opening_date_for_client(self, contact_id: int, offset: int, limit: int) \
            -> List[SubscriberContract]:
        """
        This function filter contract by contact id and sort by opening date
        :param contact_id: contact id from db
        :param offset: start pagination
        :param limit: end of pagination
        :return: List SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract)
                               .join(SubscriberContract.contacts)
                               .where(
            SubscriberContract.customer_id == contact_id,
            SubscriberContract.is_activated == True
        )
                               .offset(offset)
                               .limit(limit)
                               .order_by(SubscriberContract.opening_date)
                               ).all()

    def get_contract_where_opening_date_between_two_dates_for_admin(self, start_date: date, end_date: date, offset: int,
                                                                    limit: int) \
            -> List[SubscriberContract]:
        """
        This function filter contracts where the opening date between two date
        :param start_date: start date for filter
        :param end_date: end date
        :param offset: start of pagination
        :param limit: end of pagination
        :return: List of SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract)
                               .where(
            SubscriberContract.opening_date > start_date,
            SubscriberContract.opening_date < end_date
        )
                               .order_by(SubscriberContract.opening_date)
                               .offset(offset)
                               .limit(limit)
                               ).all()

    def get_contract_where_opening_date_between_two_dates_for_client(self, start_date: date, end_date: date,
                                                                     offset: int, limit: int) \
            -> List[SubscriberContract]:
        """
        This function filter contracts where the opening date between two dates
        :param start_date: start date for filter
        :param end_date: end date
        :param offset: start of pagination
        :param limit: end of pagination
        :return: List of SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract)
                               .where(
            SubscriberContract.opening_date > start_date,
            SubscriberContract.opening_date < end_date,
            SubscriberContract.is_activated == True
        )
                               .order_by(SubscriberContract.opening_date)
                               .offset(offset)
                               .limit(limit)
                               ).all()

    def get_contract_where_opening_date_before_given_date_for_admin(self, given_date: date,
                                                                    offset: int, limit: int) \
            -> List[SubscriberContract]:
        """
        This function filter contracts before start_date and order
        by opening date
        :param given_date: start date for filter
        :param offset: start of pagination
        :param limit: end of pagination
        :return: List of SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract)
                               .where(SubscriberContract.opening_date < given_date)
                               .order_by(SubscriberContract.opening_date)
                               .offset(offset)
                               .limit(limit)
                               ).all()

    def get_contract_where_opening_date_before_given_date_for_client(self, given_date: date,
                                                                     offset: int, limit: int) \
            -> List[SubscriberContract]:
        """
        This function filter contracts before given_date and order
        by opening date
        :param given_date: given date for filter
        :param offset: start of pagination
        :param limit: end of pagination
        :return: List of SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract)
                               .where(
            SubscriberContract.opening_date < given_date,
            SubscriberContract.is_activated == True
        )
                               .order_by(SubscriberContract.opening_date)
                               .offset(offset)
                               .limit(limit)
                               ).all()

    def get_contract_where_opening_date_after_given_date_for_admin(self, given_date: date, offset: int, limit: int) \
            -> List[SubscriberContract]:
        """
        This function filter contracts before end_date and order
        by opening date
        :param given_date: start date for filter
        :param offset: start of pagination
        :param limit: end of pagination
        :return: List of SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract)
                               .where(SubscriberContract.opening_date > given_date)
                               .order_by(SubscriberContract.opening_date)
                               .offset(offset)
                               .limit(limit)
                               ).all()

    def get_contract_where_opening_date_after_given_date_for_client(self, given_date: date, offset: int, limit: int) \
            -> List[SubscriberContract]:
        """
        This function filter contracts after given_date and order
        by opening date
        :param given_date: start date for filter
        :param offset: start of pagination
        :param limit: end of pagination
        :return: List of SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract)
                               .where(
            SubscriberContract.opening_date > given_date,
            SubscriberContract.is_activated == True
        )
                               .order_by(SubscriberContract.opening_date)
                               .offset(offset)
                               .limit(limit)
                               ).all()

    def get_contract_where_opening_date_equal_given_date_for_admin(self, given_date: date, offset: int, limit: int) \
            -> List[SubscriberContract]:
        """
        This function filter the contract where the opening date is equal to the providing given_date and order
        by opening date
        :param given_date: given date to compare
        :param offset: start of pagination
        :param limit: end of pagination
        :return: List SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract)
                               .where(SubscriberContract.opening_date == given_date)
                               .order_by(SubscriberContract.opening_date)
                               .offset(offset)
                               .limit(limit)
                               ).all()

    def get_contract_where_opening_date_equal_given_date_for_client(self, given_date: date, offset: int, limit: int) \
            -> List[SubscriberContract]:
        """
        This function filter the activated contract where the opening date is equal to the providing given_date and order
        by opening date
        :param given_date: given date to compare
        :param offset: start of pagination
        :param limit: end of pagination
        :return: List SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract)
                               .where(
            SubscriberContract.opening_date == given_date,
            SubscriberContract.is_activated == True
        )
                               .order_by(SubscriberContract.opening_date)
                               .offset(offset)
                               .limit(limit)
                               ).all()

    def get_contract_where_closing_date_before_given_date_for_admin(self, given_date: date, offset: int, limit: int) \
            -> List[SubscriberContract]:
        """
        This function filter the contract where the closing is before the providing given_date and order
        by closing date
        :param given_date: given date to compare
        :param offset: start of pagination
        :param limit: end of pagination
        :return: List SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract)
                               .where(SubscriberContract.closing_date < given_date)
                               .order_by(SubscriberContract.closing_date)
                               .offset(offset)
                               .limit(limit)
                               ).all()

    def get_contract_where_closing_date_before_given_date_for_client(self, given_date: date, offset: int, limit: int) \
            -> List[SubscriberContract]:
        """
        This function filter activated contract where the closing is before the providing given_date and order
        by closing date
        :param given_date: given date to compare
        :param offset: start of pagination
        :param limit: end of pagination
        :return: List Contract
        """
        return self.db.scalars(select(SubscriberContract)
                               .where(
            SubscriberContract.closing_date < given_date,
            SubscriberContract.is_activated == True
        )
                               .order_by(SubscriberContract.closing_date)
                               .offset(offset)
                               .limit(limit)
                               ).all()

    def get_contract_where_closing_date_after_given_date_for_admin(self, given_date: date, offset: int, limit: int) \
            -> List[SubscriberContract]:
        """
         This function filter the contract where the closing date is after  the providing given_date and order
        by closing date
        :param given_date: given date to compare
        :param offset: start of pagination
        :param limit: end of pagination
        :return: List SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract)
                               .where(SubscriberContract.closing_date > given_date)
                               .order_by(SubscriberContract.closing_date)
                               .offset(offset)
                               .limit(limit)
                               ).all()

    def get_contract_where_closing_date_after_given_date_for_client(self, given_date: date, offset: int, limit: int) \
            -> List[SubscriberContract]:
        """
         This function filter the contract where the closing date is after  the providing given_date and order
        by closing date
        :param given_date: given date to compare
        :param offset: start of pagination
        :param limit: end of pagination
        :return: List SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract)
                               .where(
            SubscriberContract.closing_date > given_date,
            SubscriberContract.is_activated == True
        )
                               .order_by(SubscriberContract.closing_date)
                               .offset(offset)
                               .limit(limit)
                               ).all()

    def get_contract_where_closing_date_equal_given_date_for_admin(self, given_date: date, offset: int, limit: int) \
            -> List[SubscriberContract]:
        """
         This function filter the contract where the closing date is equal to the providing given_date and order
        by closing date
        :param given_date: given date to compare
        :param offset: start of pagination
        :param limit: end of pagination
        :return: List SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract)
                               .where(SubscriberContract.closing_date == given_date)
                               .order_by(SubscriberContract.closing_date)
                               .offset(offset)
                               .limit(limit)
                               ).all()

    def get_contract_where_closing_date_equal_given_date_for_client(self, given_date: date, offset: int, limit: int) \
            -> List[SubscriberContract]:
        """
        This function filter activated contracts where the closing date is equal to the providing given_date and order
        by closing date
        :param given_date: given date to compare
        :param offset: start of pagination
        :param limit: end of pagination
        :return: List SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract)
                               .where(
            SubscriberContract.closing_date == given_date,
            SubscriberContract.is_activated == True
        )
                               .order_by(SubscriberContract.closing_date)
                               .offset(offset)
                               .limit(limit)
                               ).all()

    def get_contract_by_delivery_point_and_contact_uid_for_client(self, delivery_point: int, contact_uid: str) \
            -> Optional[SubscriberContract]:
        """
        This function filter an activated contract by the delivery point address and contact uid
        :param delivery_point: address of delivery point
        :param contact_uid: this is a unique contact number
        :return: return an optional of SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract).where(
            SubscriberContract.contract_uid == contact_uid,
            SubscriberContract.is_activated == True,
            SubscriberContract.infos['delivery_point'] == delivery_point
        )).first()

    def get_contract_by_delivery_point(self, delivery_point: str) -> SubscriberContract:
        """
        This function filter an activated contract by the delivery point
        :param delivery_point:
        :return: SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract).where(
            SubscriberContract.infos['delivery_point']['number'] == delivery_point,
            # SubscriberContract.is_activated ==True
        )).first()

    def get_contract_by_submitted_params(self,
                                         params: ContractDtoIncoming,
                                         offset: int,
                                         limit: int) \
            -> List[SubscriberContract]:
        """
        This function fileter a contract by submitted params
        :param agency:
        :param infos:
        :param limit:
        :param offset:
        :param params:
        :return:
        """
        return self.db.scalars(
            select(SubscriberContract).filter(
                SubscriberContract.contract_uid == params.contract_number
                if params.contract_number is not None else True
            ).join(Contacts).where(
                Contacts.contact_uid == params.customer_number
                if params.customer_number is not None else True
            )
            .offset(offset).limit(limit)
        ).all()

    def get_contracts(self, offset: int, limit: int) -> List[SubscriberContract]:
        return self.db.scalars(select(SubscriberContract).offset(offset).limit(limit)).all()