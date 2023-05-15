from typing import List, Optional, Sequence

from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from api.configs.Database import get_db_connection
from api.contact.models.ContactsModel import Contacts
from api.contact.models.SubscriberContractModel import SubscriberContract

from api.subscription.schemas.SubscriberContractSchema import ContractDtoIncoming, ContractInvoiceParams


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

    def delete_contract(self, contract: SubscriberContract) -> SubscriberContract:
        """
        To resign the contract between EDG and customer use this function,
        while resigning the table SubscriberContract will be updated with the flag
        is_activated: False.
        :param contract: the id of customer to delete
        :return: None
        """

        self.db.merge(contract)
        self.db.commit()
        return contract

    # Filters

    def get_contract_by_customer_id_for_client(self, costumer_id: int, offset: int, limit: int) -> \
            Sequence[List[SubscriberContract]]:
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
            SubscriberContract.deleted_at is not None
        ).offset(offset).limit(limit)).all()

    def get_contract_by_customer_id_for_admin(self, customer_id: int, offset: int, limit: int) \
            -> Sequence[List[SubscriberContract]]:
        """
         This function fetch all contract for the given costume_id and the given pagination where the is_activated is
         equal to True or False
        :param customer_id  from db
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
            SubscriberContract.contract_number == contract_uid,
            SubscriberContract.deleted_at == None
        )).first()

    def get_contract_by_contract_uid_for_update(self, contract_uid: str) -> SubscriberContract:
        """
        This function fetch the contract information corresponding to given contract_uid
        (unique contract ID for the contract) where is_activated is equal to True
        :param contract_uid: unique contract number
        :return:SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract).where(
            SubscriberContract.contract_number.ilike(contract_uid)
        )).first()

    def get_contract_by_contract_uid_for_admin(self, contract_uid: str) -> SubscriberContract:
        """
        This function fetch the contract information corresponding to given contract_uid
        (unique contract ID for the contract) where is_activated is equal to True or False
        :param contract_uid: unique contract number
        :return:SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract).where(
            SubscriberContract.contract_number.ilike(contract_uid.lower())
        )).first()

    def get_contract_by_contact_uid_and_contract_uid_for_client(self, contract_uid: str, contact_uid: str) \
            -> SubscriberContract:
        """
        This function is used to filter activated contracts for a specific contact by his contact number
        :param contract_uid: unique contract's ID
        :param contact_uid: contact unique ID format (CL+7chifers)
        :return: SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract).join(Contacts).where(
            SubscriberContract.contract_number.ilike(contract_uid),
            Contacts.customer_number.ilike(contact_uid),
            SubscriberContract.is_activated is True
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
            SubscriberContract.contract_number.ilike(contract_uid),
            Contacts.customer_number.ilike(contact_uid)
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
            SubscriberContract.contract_number.ilike(contract_uid),
            Contacts.infos['identity']['pid'] == contact_pid,
            SubscriberContract.is_activated is True
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
            SubscriberContract.contract_number.ilike(contract_uid),
            Contacts.customer_number.ilike(contact_pid)
        )).first()

    def get_contract_by_status_for_client(self, status: str, offset: int, limit: int) \
            -> Sequence[List[SubscriberContract]]:
        """
        This function filter the activated contract by the given status
        :param status: contract's status
        :param offset: start pagination
        :param limit: end of pagination
        :return: List of SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract).where(
            SubscriberContract.infos['status'] == status,
            SubscriberContract.is_activated is True
        ).offset(offset).limit(limit)).all()

    def get_contract_by_status_for_admin(self, status: str, offset: int, limit: int) -> \
            Sequence[List[SubscriberContract]]:
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

    def get_deleted_contract_by_status_for_admin(self, status: str, offset: int, limit: int) -> \
            Sequence[List[SubscriberContract]]:
        """
        This function filter resigned contract by the given status
        :param status:  contract's status
        :param offset: start pagination
        :param limit: end of pagination
        :return: List of SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract).where(
            SubscriberContract.infos['status'] == status
        ).offset(offset).limit(limit)).all()

    def get_contract_by_delivery_point_and_contact_uid_for_client(self, delivery_point: int, contact_uid: str) \
            -> Optional[SubscriberContract]:
        """
        This function filter an activated contract by the delivery point address and contact uid
        :param delivery_point: address of delivery point
        :param contact_uid: this is a unique contact number
        :return: return an optional of SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract).where(
            SubscriberContract.contract_number == contact_uid,
            SubscriberContract.is_activated is True,
            SubscriberContract.infos['delivery_point'] == delivery_point
        )).first()

    def get_contract_by_delivery_point_on_number(self, delivery_point: str) -> SubscriberContract:
        """
        This function filter an activated contract by the delivery point
        :param delivery_point:
        :return: SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract).where(
            SubscriberContract.infos['delivery_point']['number'] == delivery_point,
            SubscriberContract.deleted_at is None
        )).first()

    def get_contract_by_delivery_point_on_metric_number(self, metric_number: str) -> SubscriberContract:
        """
        This function filter an activated contract by the delivery point
        :param metric_number:
        :return: SubscriberContract
        """
        return self.db.scalars(select(SubscriberContract).where(
            SubscriberContract.infos['delivery_point']['metric_number'] == metric_number,
            SubscriberContract.deleted_at is None
        )).first()

    def count_contract_by_contact_number(self, contact_number: str) -> int:
        return self.db.execute(select(func.count(SubscriberContract.id)).join(Contacts).where(
            Contacts.customer_number.ilike(contact_number),
            SubscriberContract.deleted_at is not None
        )).scalar()

    def get_contract_by_submitted_params(self, params: ContractDtoIncoming, offset: int, limit: int) ->\
            Sequence[List[SubscriberContract]]:
        """
        This function fileter a contract by submitted params
        :param params:
        :param offset
        :param limit:
        :return:
        """
        return self.db.scalars(
            select(SubscriberContract).filter(
                SubscriberContract.contract_number == params.contract_number
                if params.contract_number is not None else True,
                SubscriberContract.infos['status'] == params.status.value.lower().capitalize()
                if params.status is not None else True
            ).join(Contacts).where(
                Contacts.customer_number == params.customer_number
                if params.customer_number is not None else True
            ).offset(offset).limit(limit)
        ).all()

    def count_contract(self, params: ContractDtoIncoming) -> int:
        """
        This function fileter a contract by submitted params
        :param params:
        :return:
        """
        return self.db.execute(
            select(func.count(SubscriberContract.id)).filter(
                SubscriberContract.contract_number == params.contract_number
                if params.contract_number is not None else True,
                Contacts.customer_number == params.customer_number
                if params.customer_number is not None else True,
                SubscriberContract.infos['status'] == params.status.value.lower().capitalize()
                if params.status is not None else True
            ).join(Contacts).where(
                Contacts.customer_number == params.customer_number
                if params.customer_number is not None else True
            )
        ).scalar()

    def get_contracts(self) -> Sequence[List[SubscriberContract]]:
        return self.db.scalars(select(SubscriberContract).where(SubscriberContract.is_activated is True)).all()

    def get_contract_by_contact_number(self, contact_number: str) -> Sequence[List[SubscriberContract]]:
        return self.db.scalars(select(SubscriberContract).join(Contacts).where(
            Contacts.customer_number == contact_number,
            SubscriberContract.deleted_at is not None
        )).all()

    def get_contact_contracts(self, number: str, params: ContractInvoiceParams) -> Sequence[List[SubscriberContract]]:
        return self.db.scalars(
            select(SubscriberContract)
            .where(
                SubscriberContract.contract_number == params.contract_number
                if params.contract_number is not None else True,
            ).join(
                Contacts.customer_number == number
            )
        ).all()
