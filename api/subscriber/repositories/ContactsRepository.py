from typing import List

from fastapi import Depends
from sqlalchemy import select, func, Sequence
from sqlalchemy.orm import Session

from api.configs.Database import get_db_connection
from api.subscriber.models.ContactsModel import Contacts
from api.subscriber.schemas.ContactsSchema import SearchByParams, SearchAllContact


class ContactsRepository:
    db: Session

    def __init__(
            self, db: Session = Depends(get_db_connection)
    ) -> None:
        self.db = db

    def create_contact(self, contacts: List[Contacts]) -> List[Contacts]:
        self.db.add_all(contacts)
        self.db.commit()
        return contacts

    def update_contact(self, contacts: Contacts) -> Contacts:
        self.db.merge(contacts)
        self.db.commit()
        return contacts

    def delete_contact(self, contact: Contacts) -> None:
        self.db.merge(contact)
        self.db.commit()

    def get_contact_by_id_for_client(self, id: int) -> Contacts:
        return self.db.scalars(select(Contacts).where(Contacts.id == id, Contacts.is_activated == True)).first()

    def get_contact_by_id_for_admin(self, id: int) -> Contacts:
        query = select(Contacts).where(Contacts.id == id)
        return self.db.scalars(select(Contacts).where(Contacts.id == id)).first()

    def get_contact_by_pid_for_admin(self, pid: str) -> Contacts:
        return self.db.scalars(select(Contacts).where(
            Contacts.infos['identity']['pid'] == pid
        )).first()

    def get_contacts_for_admin(self) -> List[Contacts]:
        return self.db.scalars(select(Contacts).order_by(Contacts.id)).all()

    def get_contact_by_email_for_admin(self, email: str) -> Contacts:
        return self.db.scalars(select(Contacts).where(
            Contacts.infos["address"]["email"] == email
        )).first()

    def get_contact_by_phone_for_admin(self, telephone: str) -> Contacts:
        return self.db.scalars(select(Contacts).where(
            telephone == Contacts.infos['address']['telephone']
        )).first()

    def get_contact_by_pid_for_client(self, pid: str) -> Contacts:
        return self.db.scalars(select(Contacts).where(
            Contacts.infos['identity']['pid'] == pid,
            Contacts.is_activated == True
        )).first()

    def get_contact_by_phone_for_client(self, telephone: str) -> Contacts:
        return self.db.scalars(select(Contacts).where(
            telephone == Contacts.infos['address']['telephone'],
            Contacts.is_activated == True
        )).first()

    def get_contacts_for_client(self, type_contact: SearchAllContact) -> List[Contacts]:
        return self.db.scalars(select(Contacts).where(
            Contacts.infos['status'] == type_contact.type
            if type_contact.type is not None else True,
            Contacts.is_activated == type_contact.status
            if type_contact.status is not None else True
        )).all()

    def get_contact_by_email_for_client(self, email: str) -> Contacts:
        return self.db.scalars(select(Contacts).where(
            Contacts.infos["address"]["email"] == email,
            Contacts.is_activated == True
        )).first()

    def get_contact_by_uid_for_client(self, contact_uid: str) -> Contacts:
        return self.db.scalars(select(Contacts).where(
            Contacts.customer_number == contact_uid,
            Contacts.is_activated == True
        )).first()

    def get_contact_by_uid_for_admin(self, contact_uid: str) -> Contacts:
        return self.db.scalars(select(Contacts).where(
            Contacts.contact_uid.ilike(contact_uid)
        )).first()

    def get_contact_by_type_for_admin(self, contact_type: str, offset: int, limit: int) -> List[Contacts]:
        return self.db.scalars(select(Contacts).where(
            Contacts.infos['type'] == contact_type.lower().capitalize()
        ).offset(offset).limit(limit)).all()

    def get_contact_by_type_for_client(self, contact_type: str, offset: int, limit: int) -> List[Contacts]:
        return self.db.scalars(select(Contacts).where(
            Contacts.infos['type'] == contact_type.lower().capitalize(),
            Contacts.is_activated == True
        ).offset(offset).limit(limit)).all()

    def get_contacts_for_client(self, offset: int, limit: int, type_contact: SearchAllContact) -> Sequence[List[Contacts]]:
        return self.db.scalars(select(Contacts).where(
            Contacts.is_activated == type_contact.status
            if type_contact.status is not None else True,
            Contacts.infos['type'] == type_contact.type.lower().capitalize()
            if type_contact.type is not None else True
        ).offset(offset).limit(limit)).all()

    def count_contact(self, type_contact: SearchAllContact) -> int:
        return self.db.execute(select(func.count(Contacts.id)).where(
            Contacts.is_activated == type_contact.status
            if type_contact.status is not None else True,
            Contacts.infos['type'] == type_contact.type.lower().capitalize()
            if type_contact.type is not None else True
        )).scalar()

    def search_contact_by_param(self, query_params: SearchByParams) -> Contacts:
        return self.db.scalars(select(Contacts).filter(
            Contacts.is_activated == query_params.status
            if query_params.status is not None else True,
            Contacts.infos['identity']['pid'] == query_params.pid
            if query_params.pid is not None else True,
            Contacts.infos['address']['telephone'] == query_params.phone
            if query_params.phone is not None else True,
            Contacts.infos['address']['email'] == query_params.email
            if query_params.email is not None else True,
            Contacts.customer_number.ilike(query_params.customer_number)
            if query_params.customer_number is not None else True
        )).first()

    def get_contact_by_number(self, number: str) -> Contacts:
        return self.db.scalars(
            select(Contacts).where(Contacts.customer_number == number)
        ).first()
