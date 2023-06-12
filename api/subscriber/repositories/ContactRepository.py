from typing import List

from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from api.configs.Database import get_db_connection
from api.subscriber.models.ContactModel import Contact
from api.subscriber.schemas.ContactSchema import SearchByParams, SearchAllContact


class ContactRepository:
    db: Session

    def __init__(
            self, 
            db: Session = Depends(get_db_connection)
    ) -> None:
        self.db = db

    def create_contact(self, contacts: List[Contact]) -> List[Contact]:
        self.db.add_all(contacts)
        self.db.commit()
        return contacts

    def update_contact(self, contacts: Contact) -> Contact:
        self.db.merge(contacts)
        self.db.commit()
        return contacts

    def delete_contact(self, contact: Contact) -> None:
        self.db.merge(contact)
        self.db.commit()

    def get_contact_by_id_for_client(self, id: int) -> Contact:
        return self.db.scalars(select(Contact).where(Contact.id == id, Contact.is_activated == True)).first()

    def get_contact_by_id_for_admin(self, id: int) -> Contact:
        return self.db.scalars(select(Contact).where(Contact.id == id)).first()

    def get_contact_by_pid_for_admin(self, pid: str) -> Contact:
        return self.db.scalars(select(Contact).where(
            Contact.infos['identity']['pid'] == pid
        )).first()

    def get_contacts_for_admin(self) -> List[Contact]:
        return self.db.scalars(select(Contact).order_by(Contact.id)).all()

    def get_contact_by_email_for_admin(self, email: str) -> Contact:
        return self.db.scalars(select(Contact).where(
            Contact.infos["address"]["email"] == email
        )).first()

    def get_contact_by_phone_for_admin(self, telephone: str) -> Contact:
        return self.db.scalars(select(Contact).where(
            telephone == Contact.infos['address']['telephone']
        )).first()

    def get_contact_by_pid_for_client(self, pid: str) -> Contact:
        return self.db.scalars(select(Contact).where(
            Contact.infos['identity']['pid'] == pid,
            Contact.is_activated == True
        )).first()

    def get_contact_by_phone_for_client(self, telephone: str) -> Contact:
        return self.db.scalars(select(Contact).where(
            telephone == Contact.infos['address']['telephone'],
            Contact.is_activated == True
        )).first()

    def get_contacts_for_client(self, type_contact: SearchAllContact) -> List[Contact]:
        return self.db.scalars(select(Contact).where(
            Contact.infos['status'] == type_contact.type
            if type_contact.type is not None else True,
            Contact.is_activated == type_contact.status
            if type_contact.status is not None else True
        )).all()

    def get_contact_by_email_for_client(self, email: str) -> Contact:
        return self.db.scalars(select(Contact).where(
            Contact.infos["address"]["email"] == email,
            Contact.is_activated == True
        )).first()

    def get_contact_by_uid_for_client(self, contact_uid: str) -> Contact:
        return self.db.scalars(select(Contact).where(
            Contact.customer_number == contact_uid,
            Contact.is_activated == True
        )).first()

    def get_contact_by_uid_for_admin(self, contact_uid: str) -> Contact:
        return self.db.scalars(select(Contact).where(
            Contact.contact_uid.ilike(contact_uid)
        )).first()

    def get_contact_by_type_for_admin(self, contact_type: str, offset: int, limit: int) -> List[Contact]:
        return self.db.scalars(select(Contact).where(
            Contact.infos['type'] == contact_type.lower().capitalize()
        ).offset(offset).limit(limit)).all()

    def get_contact_by_type_for_client(self, contact_type: str, offset: int, limit: int) -> List[Contact]:
        return self.db.scalars(select(Contact).where(
            Contact.infos['type'] == contact_type.lower().capitalize(),
            Contact.is_activated == True
        ).offset(offset).limit(limit)).all()
    def get_contacts_for_client(self, offset: int, limit: int, type_contact: SearchAllContact) -> List[Contact]:
        return self.db.scalars(select(Contact).where(
            Contact.is_activated == type_contact.status
            if type_contact.status is not None else True,
            Contact.infos['type'] == type_contact.type.lower().capitalize()
            if type_contact.type is not None else True
        ).offset(offset).limit(limit)).all()

    def count_contact(self, type_contact: SearchAllContact) -> int:
        return self.db.execute(select(func.count(Contact.id)).where(
            Contact.is_activated == type_contact.status
            if type_contact.status is not None else True,
            Contact.infos['type'] == type_contact.type.lower().capitalize()
            if type_contact.type is not None else True
        )).scalar()

    def search_contact_by_param(self, query_params: SearchByParams) -> Contact:
        return self.db.scalars(select(Contact).filter(
            Contact.is_activated == query_params.status
            if query_params.status is not None else True,
            Contact.infos['identity']['pid'] == query_params.pid
            if query_params.pid is not None else True,
            Contact.infos['address']['telephone'] == query_params.phone
            if query_params.phone is not None else True,
            Contact.infos['address']['email'] == query_params.email
            if query_params.email is not None else True,
            Contact.customer_number.ilike(query_params.customer_number)
            if query_params.customer_number is not None else True
        )).first()

    def get_contact_by_number(self, number: str) -> Contact:
        return self.db.scalars(
            select(Contact).where(Contact.customer_number == number)
        ).first()
        
     # get maximum number of contact
    def getmaxnumber(self) -> int:
        max_number = (
            self.db.query(func.max(Contact.customer_number))
            .one()[0]
        )
        return 0 if max_number is None else max_number
