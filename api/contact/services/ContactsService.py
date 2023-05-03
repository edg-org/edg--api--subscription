import json
import logging
import re
from datetime import date
from typing import List

from fastapi import Depends
from sqlalchemy import String

from api.exceptions import RepeatingIdentityPid, PhoneNumberExist, EmailExist, IdentityPidExist, IdentityPidNotFound, \
    ContactNotFound
from api.contact.models.ContactsModel import Contacts
from api.contact.repositories.ContactsRepository import ContactsRepository
from api.contact.schemas.pydantic.ContactsSchema import ContactsInputDto, ContactOutputDto
from api.contact.services.GuidGenerator import GuidGenerator


def buildContractOutputDto(contact: Contacts):
    return ContactOutputDto(
        id=contact.id,
        infos=contact.infos,
        is_activated=contact.is_activated,
        contact_uid=contact.contact_uid,
        created_at=contact.created_at,
        updated_at=contact.updated_at,
        deleted_at=contact.deleted_at
    )


class ContactsService:
    contacts_repository: ContactsRepository

    def __init__(self, contacts_repository: ContactsRepository = Depends()) -> None:
        self.contacts_repository = contacts_repository

    def create_contact(self, contact_body: List[ContactsInputDto]) -> List[ContactOutputDto]:
        # Convertissons notre object en json

        # Transform contract_schema to a list
        logging.error("message %s", type(contact_body))
        contact_body = [c.infos.dict() for c in contact_body]
        logging.error("message %s", contact_body)
        logging.error("message %s", type(contact_body))
        contact_body = json.loads(json.dumps(contact_body, default=str))
        logging.error("sd %s ", contact_body)

        # Check if there are repeating identity pid, if true, then the len of identity_pid will be different
        # to the len of contact_body
        identity_pid = set()
        for c in contact_body:
            identity_pid.add(c['identity']['pid'])
        if len(identity_pid) != len(contact_body):
            raise RepeatingIdentityPid

        contacts: List[Contacts] = [self.check_save_business_logic(c) for c in contact_body]
        contacts = self.contacts_repository.create_contact(contacts)

        return [buildContractOutputDto(c) for c in contacts]

    def check_save_business_logic(self, contact_body: ContactsInputDto) -> Contacts:
        # contact_body = json.loads(contact_body.json())
        '''
            Pour ne pas ajouter deux utilisateur avec utilisant le meme numero
            email et la carte d'identite nous procedons a la verification dans la base 
            de donne et retournons un message d'erreur au cas ou les donnees sont deja 
            retrouvees dans la bd
        '''
        if self.contacts_repository.get_contact_by_phone_for_admin(
                contact_body['address']['telephone']) is not None:
            raise PhoneNumberExist
        if self.contacts_repository.get_contact_by_email_for_admin(contact_body['address']['email']) is not None:
            raise EmailExist
        if self.contacts_repository.get_contact_by_pid_for_admin(contact_body['identity']['pid']) is not \
                None:
            raise IdentityPidExist
        return Contacts(
            infos=contact_body,
            contact_uid=GuidGenerator.contactUID(contact_body['identity']['pid']),
            created_at=date.today()
        )

    def update_contact(self, pid: str, contact_body: ContactsInputDto) -> ContactOutputDto:
        # Convertissons notre object en json
        contact_body.infos = json.loads(contact_body.infos.json())
        '''
            La modification est effectuer par le numero d'identifiant unique (passport ou carte d'identite) 
            pour ce fait nous verifions l'existance de l'utilisateur dans la bd, au cas ou il n'existe pas 
            on retourne une erreur 403
        '''
        contact: Contacts = self.contacts_repository.get_contact_by_pid_for_admin(pid)
        checkIdentity: Contacts = self.contacts_repository.get_contact_by_pid_for_admin(
            contact_body.infos['identity']['pid'])
        if contact is None:
            raise IdentityPidNotFound
        if checkIdentity is not None:
            if checkIdentity.infos['identity']['pid'] != pid:
                raise IdentityPidExist
        # Pendant la modification nous verifions si le numero modifie n'existe pas dans la bd
        contactByPhone: Contacts = self.contacts_repository.get_contact_by_phone_for_admin(
            contact_body.infos['address']['telephone'])
        if contactByPhone is not None:
            if contactByPhone.contact_uid != contact.contact_uid:
                raise PhoneNumberExist

        # Pendant la modification nous verifions si l'email modifie n'existe pas dans la bd
        contactByEmail: Contacts = self.contacts_repository.get_contact_by_email_for_admin(
            contact_body.infos['address']['email'])
        if contactByEmail is not None:
            if contactByEmail.contact_uid != contact.contact_uid:
                raise EmailExist

        return buildContractOutputDto(self.contacts_repository.update_contact(
            Contacts(
                infos=contact_body.infos,
                updated_at=date.today(),
                created_at=contact.created_at,
                deleted_at=contact.deleted_at,
                is_activated=contact.is_activated,
                id=contact.id,
                contact_uid=contact.contact_uid,
            )
        ))

    def delete_contact(self, pid: str) -> None:
        contact = self.contacts_repository.get_contact_by_pid_for_client(pid)
        if contact is None:
            raise IdentityPidNotFound
        contact.is_activated = False
        contact.deleted_at = date.today()
        self.contacts_repository.delete_contact(
            contact
        )

    def get_contact_by_id_for_admin(self, id: int) -> ContactOutputDto:
        c: Contacts = self.contacts_repository.get_contact_by_id_for_admin(id)
        if c is None:
            raise ContactNotFound
        return buildContractOutputDto(c)

    def get_contact_by_pid_for_admin(self, pid: str) -> ContactOutputDto:
        c = self.contacts_repository.get_contact_by_pid_for_admin(pid)
        if c is not None:
            return buildContractOutputDto(c)
        else:
            raise ContactNotFound

    def get_contact_by_pid_for_client(self, pid: str) -> ContactOutputDto:
        c = self.contacts_repository.get_contact_by_pid_for_client(pid)
        if c is not None:
            return buildContractOutputDto(c)
        else:
            raise ContactNotFound

    def get_contacts_for_admin(self, offset: int, limit: int) -> List[ContactOutputDto]:
        contacts: List[Contacts] = self.contacts_repository.get_contacts_for_admin(offset, limit)
        if len(contacts) != 0:
            return [buildContractOutputDto(c) for c in contacts]
        else:
            raise ContactNotFound

    def get_contacts_for_client(self, offset: int, limit: int) -> List[ContactOutputDto]:
        contacts: List[Contacts] = self.contacts_repository.get_contacts_for_client(offset, limit)
        if len(contacts) != 0:
            return [buildContractOutputDto(c) for c in contacts]
        else:
            raise ContactNotFound

    def get_contact_by_email_for_admin(self, email: str) -> ContactOutputDto:
        c = self.contacts_repository.get_contact_by_email_for_admin(email)
        if c is not None:
            return buildContractOutputDto(c)
        else:
            raise EmailExist

    def get_contact_by_email_for_client(self, email: str) -> ContactOutputDto:
        c = self.contacts_repository.get_contact_by_email_for_client(email)
        if c is not None:
            return buildContractOutputDto(c)
        else:
            raise ContactNotFound

    def get_contact_by_phone_for_admin(self, telephone: str) -> ContactOutputDto:
        # logging.error(f" phone format %s ", self.phoneNumberFormat(telephone))
        c = self.contacts_repository.get_contact_by_phone_for_admin(self.phoneNumberFormat(telephone))
        if c is not None:
            return buildContractOutputDto(c)
        else:
            raise ContactNotFound

    """ Cette fonction nous permet de formater le numero de telephone au format
        Guineen +224-610-15-96-20, pour etre utilise pour les fins de comparaison avec 
        celle de la bd
       """

    def get_contact_by_phone_for_client(self, telephone: str) -> ContactOutputDto:
        # logging.error(f" phone format %s ", self.phoneNumberFormat(telephone))
        c = self.contacts_repository.get_contact_by_phone_for_client(self.phoneNumberFormat(telephone))
        if c is not None:
            return buildContractOutputDto(c)
        else:
            raise ContactNotFound

    def phoneNumberFormat(self, phoneNumber: str) -> String:
        if phoneNumber.startswith("+224") and not re.compile("^\+224-\d{3}-\d{2}-\d{2}-\d{2}$").match(phoneNumber):
            phoneNumber = phoneNumber[:4] + "-" + phoneNumber[4:7] + "-" + phoneNumber[7:9] + "-" + phoneNumber[9:11] \
                          + "-" + phoneNumber[11:13]
        if not phoneNumber.startswith("+224") and not re.compile("^\+224-\d{3}-\d{2}-\d{2}-\d{2}$").match(phoneNumber):
            phoneNumber = "+224-" + phoneNumber[:3] + "-" + phoneNumber[3:5] + "-" + phoneNumber[5:7] \
                          + "-" + phoneNumber[7:9]

        return phoneNumber

    def get_contact_by_uid_for_client(self, contact_uid: str) -> ContactOutputDto:
        c = self.contacts_repository.get_contact_by_uid_for_client(contact_uid)
        if c is None:
            raise ContactNotFound
        return buildContractOutputDto(c)

    def get_contact_by_uid_for_admin(self, contact_uid: str) -> ContactOutputDto:
        c = self.contacts_repository.get_contact_by_uid_for_admin(contact_uid)
        if c is None:
            raise ContactNotFound
        return buildContractOutputDto(c)

    def get_contact_by_id_for_client(self, id: int) -> ContactOutputDto:
        c = self.contacts_repository.get_contact_by_id_for_client(id)
        if c is None:
            raise ContactNotFound
        return buildContractOutputDto(c)

    def get_contact_by_type_for_admin(self, contact_type: str, offset: int, limit: int) -> List[ContactOutputDto]:
        contacts: List[Contacts] = self.contacts_repository.get_contact_by_type_for_admin(contact_type, offset, limit)
        if len(contacts) == 0:
            raise ContactNotFound
        return [buildContractOutputDto(c) for c in contacts]

    def get_contact_by_type_for_client(self, contact_type: str, offset: int, limit: int) -> List[ContactOutputDto]:
        contacts: List[Contacts] = self.contacts_repository.get_contact_by_type_for_client(contact_type, offset, limit)
        if len(contacts) == 0:
            raise ContactNotFound
        return [buildContractOutputDto(c) for c in contacts]
