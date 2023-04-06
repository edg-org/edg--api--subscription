import datetime
import json
import string
from typing import Dict, Optional, List, cast, Sequence

from fastapi import Depends
from sqlalchemy import select, String, Row, Sequence
from sqlalchemy.orm import Session, lazyload

from api.configs.Database import get_db_connection
from api.models.ContactsModel import Contacts


class ContactsRepository:
    db: Session

    def __init__(
            self, db: Session = Depends(get_db_connection)
    ) -> None:
        self.db = db

    def create_contact(self, contact: Contacts) -> Contacts:
        self.db.add(contact)
        self.db.commit()
        self.db.refresh(contact)
        return contact

    def update_contact(self, contacts: Contacts) -> Contacts:
        self.db.merge(contacts)
        self.db.commit()
        return contacts

    def delete_contact(self, contact: Contacts) -> None:
        self.db.merge(contact)
        self.db.commit()

    def get_contact_by_id_for_client(self, id: int) -> Contacts:
        query = select(Contacts).where(Contacts.id == id, Contacts.is_activated == True)
        return self.db.scalars(query).first()

    def get_contact_by_id_for_admin(self, id: int) -> Contacts:
        query = select(Contacts).where(Contacts.id == id)
        return self.db.scalars(query).first()

    def get_contact_by_pid_for_admin(self, pid: str) -> Contacts:
        return self.db.scalars(select(Contacts).where(
            Contacts.infos['identity']['pid'] == pid
        )).first()

    def get_contacts_for_admin(self, offset: int = 0, limit: int = 10) -> List[Contacts]:
        return self.db.scalars(select(Contacts).offset(offset).limit(limit)).all()

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

    def get_contacts_for_client(self, offset: int, limit: int) -> List[Contacts]:
        return self.db.scalars(select(Contacts).where(Contacts.is_activated == True).offset(offset).limit(limit)).all()

    def get_contact_by_email_for_client(self, email: str) -> Contacts:
        return self.db.scalars(select(Contacts).where(
            Contacts.infos["address"]["email"] == email,
            Contacts.is_activated == True
        )).first()

    def get_contact_by_uid_for_client(self, contact_uid: str) -> Contacts:
        return self.db.scalars(select(Contacts).where(
            Contacts.contact_uid.ilike(contact_uid),
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