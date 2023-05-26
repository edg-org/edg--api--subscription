from typing import List, Optional, Sequence

from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from api.configs.Database import get_db_connection
from api.subscriber.models.ContactsModel import Contacts
from api.subscription.models.ContractModel import Contract

from api.subscription.schemas.ContractSchema import ContractInvoiceParams, ContractDtoQueryParams


class ContractRepository:
    db: Session

    def __init__(self, db: Session = Depends(get_db_connection)) -> None:
        self.db = db

    def create_contract(self, contract: List[Contract]) -> List[Contract]:
        """
        This function is designed to create a new subscriber's contract, it received  as
        :param contract: is an ORM model of the table contract that own
        all information about contract
        :return: Contract
        """
        self.db.add_all(contract)
        self.db.commit()
        return contract

    def update_contract(self, contract: Contract) -> Contract:
        """
        This function is used to update user information from the Contract table
        :param contract: is an ORM model of the table contract that own
        all information about contract
        :return: Contract
        """
        self.db.merge(contract)
        self.db.commit()
        return contract

    def delete_contract(self, contract: Contract) -> Contract:
        """
        To resign the contract between EDG and customer use this function,
        while resigning the table Contract will be updated with the flag
        is_activated: False.
        :param contract: the id of customer to delete
        :return: None
        """

        self.db.merge(contract)
        self.db.commit()
        return contract

    # Filters

    def get_contract_by_customer_id_for_client(self, costumer_id: int, offset: int, limit: int) -> \
            Sequence[List[Contract]]:
        """
        This function fetch all contract for the given costume_id and the given pagination where the is_activated is
        equal to True
        :param costumer_id: customer id from db
        :param offset: start of pagination
        :param limit: end of pagination
        :return: List of Contract
        """
        return self.db.scalars(select(Contract).where(
            Contract.customer_id == costumer_id,
            Contract.deleted_at is not None
        ).offset(offset).limit(limit)).all()

    def get_contract_by_customer_id_for_admin(self, customer_id: int, offset: int, limit: int) \
            -> Sequence[List[Contract]]:
        """
         This function fetch all contract for the given costume_id and the given pagination where the is_activated is
         equal to True or False
        :param customer_id  from db
        :param offset: start pagination
        :param limit: end pagination
        :return: List of Contract
        """
        return self.db.scalars(select(Contract).where(
            Contract.customer_id == customer_id
        ).offset(offset).limit(limit)).all()

    def get_contract_by_contract_uid(self, contract_uid: str) -> Contract:
        """
        This function fetch the contract information corresponding to given contract_uid
        (unique contract ID for the contract) where is_activated is equal to True
        :param contract_uid: unique contract number
        :return:Contract
        """
        return self.db.scalars(select(Contract).where(
            Contract.contract_number == contract_uid,
            Contract.deleted_at == None
        )).first()

    def get_contract_by_contract_uid_for_update(self, contract_uid: str) -> Contract:
        """
        This function fetch the contract information corresponding to given contract_uid
        (unique contract ID for the contract) where is_activated is equal to True
        :param contract_uid: unique contract number
        :return:Contract
        """
        return self.db.scalars(select(Contract).where(
            Contract.contract_number.ilike(contract_uid)
        )).first()

    def get_contract_by_contract_uid_for_admin(self, contract_uid: str) -> Contract:
        """
        This function fetch the contract information corresponding to given contract_uid
        (unique contract ID for the contract) where is_activated is equal to True or False
        :param contract_uid: unique contract number
        :return:Contract
        """
        return self.db.scalars(select(Contract).where(
            Contract.contract_number.ilike(contract_uid.lower())
        )).first()

    def get_contract_by_contact_uid_and_contract_uid_for_client(self, contract_uid: str, contact_uid: str) \
            -> Contract:
        """
        This function is used to filter activated contracts for a specific contact by his contact number
        :param contract_uid: unique contract's ID
        :param contact_uid: contact unique ID format (CL+7chifers)
        :return: Contract
        """
        return self.db.scalars(select(Contract).join(Contacts).where(
            Contract.contract_number.ilike(contract_uid),
            Contacts.customer_number.ilike(contact_uid),
            Contract.is_activated is True
        )).first()

    def get_contract_by_contact_uid_and_contract_uid_for_admin(self, contract_uid: str, contact_uid: str) \
            -> Contract:
        """
        This function is used to filter contracts (activated and disabled) for a specific contact by his contact number
        :param contract_uid: unique contract's ID
        :param contact_uid: contact unique ID format (CL+7chifers)
        :return: Contract
        """
        return self.db.scalars(select(Contract).join(Contacts).where(
            Contract.contract_number.ilike(contract_uid),
            Contacts.customer_number.ilike(contact_uid)
        )).first()

    def get_contract_by_contact_pid_and_contract_uid_for_client(self, contract_uid: str,
                                                                contact_pid: str) -> Contract:
        """
        This function filter the activated contracts for a specific contact pid
        (personal identity number of contact is can be passport number or ID number)
        :param contract_uid: unique contract's ID
        :param contact_pid: contact identity number (pid from Passport or ID)
        :return: Contract
        """
        return self.db.scalars(select(Contract).join(Contacts).where(
            Contract.contract_number.ilike(contract_uid),
            Contacts.infos['identity']['pid'] == contact_pid,
            Contract.is_activated is True
        )).first()

    def get_contract_by_contact_pid_and_contract_uid_for_admin(self, contract_uid: str,
                                                               contact_pid: str) -> Contract:
        """
        This function filter the activated contracts for a specific contact pid
        (personal identity number of contact is can be passport number or ID number)
        :param contract_uid: unique contract's ID
        :param contact_pid: contact identity number (pid from Passport or ID)
        :return: Contract
        """
        return self.db.scalars(select(Contract).join(Contacts).where(
            Contract.contract_number.ilike(contract_uid),
            Contacts.customer_number.ilike(contact_pid)
        )).first()

    def get_contract_by_status_for_client(self, status: str, offset: int, limit: int) \
            -> Sequence[List[Contract]]:
        """
        This function filter the activated contract by the given status
        :param status: contract's status
        :param offset: start pagination
        :param limit: end of pagination
        :return: List of Contract
        """
        return self.db.scalars(select(Contract).where(
            Contract.infos['status'] == status,
            Contract.is_activated is True
        ).offset(offset).limit(limit)).all()

    def get_contract_by_status_for_admin(self, status: str, offset: int, limit: int) -> \
            Sequence[List[Contract]]:
        """
        This function filter activated or resigned contract by the given status
        :param status:  contract's status
        :param offset: start pagination
        :param limit: end of pagination
        :return: List of Contract
        """
        return self.db.scalars(select(Contract).where(
            Contract.infos['status'] == status
        ).offset(offset).limit(limit)).all()

    def get_deleted_contract_by_status_for_admin(self, status: str, offset: int, limit: int) -> \
            Sequence[List[Contract]]:
        """
        This function filter resigned contract by the given status
        :param status:  contract's status
        :param offset: start pagination
        :param limit: end of pagination
        :return: List of Contract
        """
        return self.db.scalars(select(Contract).where(
            Contract.infos['status'] == status
        ).offset(offset).limit(limit)).all()

    def get_contract_by_delivery_point_and_contact_uid_for_client(self, delivery_point: int, contact_uid: str) \
            -> Optional[Contract]:
        """
        This function filter an activated contract by the delivery point address and contact uid
        :param delivery_point: address of delivery point
        :param contact_uid: this is a unique contact number
        :return: return an optional of Contract
        """
        return self.db.scalars(select(Contract).where(
            Contract.contract_number == contact_uid,
            Contract.is_activated is True,
            Contract.infos['delivery_point'] == delivery_point
        )).first()

    def get_contract_by_delivery_point_on_number(self, delivery_point: str) -> Contract:
        """
        This function filter an activated contract by the delivery point
        :param delivery_point:
        :return: Contract
        """
        return self.db.scalars(select(Contract).where(
            Contract.infos['delivery_point']['number'] == delivery_point,
            Contract.deleted_at == None
        )).first()

    def get_contract_by_delivery_point_on_metric_number(self, metric_number: str) -> Contract:
        """
        This function filter an activated contract by the delivery point
        :param metric_number:
        :return: Contract
        """
        return self.db.scalars(select(Contract).where(
            Contract.infos['delivery_point']['metric_number'] == metric_number,
            Contract.deleted_at == None
        )).first()

    def count_contract_by_contact_number(self, contact_number: str) -> int:
        return self.db.execute(select(func.count(Contract.id)).join(Contacts).where(
            Contacts.customer_number.ilike(contact_number),
            Contract.deleted_at is not None
        )).scalar()

    def get_contract_by_submitted_params(self, params: ContractDtoQueryParams, offset: int, limit: int) ->\
            Sequence[List[Contract]]:
        """
        This function fileter a contract by submitted params
        :param params:
        :param offset
        :param limit:
        :return:
        """
        return self.db.scalars(
            select(Contract).filter(
                Contract.contract_number == params.contract_number
                if params.contract_number is not None else True,
                Contract.infos['status'] == params.status.value.lower().capitalize()
                if params.status is not None else True
            ).join(Contacts).where(
                Contacts.customer_number == params.customer_number
                if params.customer_number is not None else True
            ).offset(offset).limit(limit)
        ).all()

    def count_contract(self, params: ContractDtoQueryParams) -> int:
        """
        This function fileter a contract by submitted params
        :param params:
        :return:
        """
        return self.db.execute(
            select(func.count(Contract.id)).filter(
                Contract.contract_number == params.contract_number
                if params.contract_number is not None else True,
                Contacts.customer_number == params.customer_number
                if params.customer_number is not None else True,
                Contract.infos['status'] == params.status.value.lower().capitalize()
                if params.status is not None else True
            ).join(Contacts).where(
                Contacts.customer_number == params.customer_number
                if params.customer_number is not None else True
            )
        ).scalar()

    def get_contracts(self) -> Sequence[List[Contract]]:
        return self.db.scalars(select(Contract).where(Contract.is_activated is True)).all()

    def get_contract_by_contact_number(self, contact_number: str) -> Sequence[List[Contract]]:
        return self.db.scalars(select(Contract).join(Contacts).where(
            Contacts.customer_number == contact_number,
            Contract.deleted_at is not None
        )).all()

    def get_contact_contracts(self, number: str, params: ContractInvoiceParams) -> Sequence[List[Contract]]:
        return self.db.scalars(
            select(Contract)
            .where(
                Contract.contract_number == params.contract_number
                if params.contract_number is not None else True
            ).join(
                Contacts
            ).where(Contacts.customer_number == number)
        ).all()


