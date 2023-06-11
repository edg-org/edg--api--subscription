import re
import json
import logging
from typing import List
from fastapi import Depends
from datetime import datetime
from sqlalchemy import String
from api.subscriber.models.ContactsModel import Contacts
from api.subscriber.repositories.ContactsRepository import ContactsRepository
from api.exceptions import (
    EmailExist, 
    RepeatingEmail,
    ContactIsDisable,
    ContactNotFound,
    SearchParamError,
    PhoneNumberExist, 
    IdentityPidExist,
    RepeatingPhoneNumber,
    RepeatingIdentityPid,
)
from api.subscriber.schemas.ContactsSchema import (
    SearchByParams,
    SearchAllContact,
    ContactOutputDto,
    ContactsInputDto,
    ContactsInputUpdateDto,
    ContactDtoWithPagination
)
from api.utilis.GuidGenerator import GuidGenerator

class ContactsService:
    contacts_repository: ContactsRepository
    def __init__(self, contacts_repository: ContactsRepository = Depends()) -> None:
        self.contacts_repository = contacts_repository

    def create_contact(self, contact_body: List[ContactsInputDto]) -> List[ContactOutputDto]:
        # Conversations notre object en json
        # Transform contract_schema to a list
        contact_body = [c.dict() for c in contact_body]
        contact_body = json.loads(json.dumps(contact_body, default=str))
        # Check if there are repeating identity pid, email or phone number, if true, then the len of identity_pid
        # will be different to the len of contact_body
        check_repeating = set()
        for c in contact_body:
            check_repeating.add(c['identity']['pid'])
        if len(check_repeating) != len(contact_body):
            raise RepeatingIdentityPid
        check_repeating = set()
        for c in contact_body:
            check_repeating.add(c['address']['email'])
        if len(check_repeating) != len(contact_body):
            raise RepeatingEmail
        check_repeating = set()
        for c in contact_body:
            check_repeating.add(c['address']['telephone'])
        if len(check_repeating) != len(contact_body):
            raise RepeatingPhoneNumber

        contacts: List[Contacts] = [self.check_save_business_logic(c) for c in contact_body]
        contacts = self.contacts_repository.create_contact(contacts)

        return [self.buildContractOutputDto(c) for c in contacts]

    def check_save_business_logic(self, contact_body: ContactsInputDto) -> Contacts:
        '''
            Pour ne pas ajouter deux utilisateur avec utilisant le meme numero
            email et la carte d'identite nous procedons a la verification dans la base 
            de donne et retournons un message d'erreur au cas ou les donnees sont deja 
            retrouvees dans la bd
        '''
        find_duplicate = self.contacts_repository.get_contact_by_phone_for_admin(
                contact_body['address']['telephone'])
        if find_duplicate is not None:
            raise PhoneNumberExist(find_duplicate.infos['address']['telephone'])
        find_duplicate = self.contacts_repository.get_contact_by_email_for_admin(contact_body['address']['email'])
        if find_duplicate is not None:
            raise EmailExist(find_duplicate.infos['address']['email'])
        find_duplicate = self.contacts_repository.get_contact_by_pid_for_admin(contact_body['identity']['pid'])
        if find_duplicate is not None:
            raise IdentityPidExist(find_duplicate.infos['identity']['pid'])
        
        max_number = self.contacts_repository.getmaxnumber()
        if max_number == 0:
            code = 10000000
            
        return Contacts(
            infos=contact_body,
            customer_number=customer_number
        )

    def update_contact(self, number: str, contact_body: ContactsInputUpdateDto) -> ContactOutputDto:
        # Convertissons notre object en json
        contact_body = json.loads(contact_body.json())
        '''
            La modification est effectuer par le numero d'identifiant unique (passport ou carte d'identite) 
            pour ce fait nous verifions l'existance de l'utilisateur dans la bd, au cas ou il n'existe pas 
            on retourne une erreur 403
        '''
        contact: Contacts = self.contacts_repository.get_contact_by_number(number)
        if contact is None:
            raise ContactNotFound

        checkIdentity: Contacts = self.contacts_repository.get_contact_by_pid_for_admin(
            contact_body['identity']['pid'])
        if checkIdentity is not None:
            if checkIdentity.infos['identity']['pid'] != contact.infos['identity']['pid']:
                raise IdentityPidExist
        # check before any modification if the contact is disable or not
        if contact.deleted_at is not None:
            raise ContactIsDisable
        # Pendant la modification nous verifions si le numero modifie n'existe pas dans la bd
        contactByPhone: Contacts = self.contacts_repository.get_contact_by_phone_for_admin(
            contact_body['address']['telephone'])
        if contactByPhone is not None:
            if contactByPhone.customer_number != contact.customer_number:
                raise PhoneNumberExist

        # Pendant la modification nous verifions si l'email modifie n'existe pas dans la bd
        contactByEmail: Contacts = self.contacts_repository.get_contact_by_email_for_admin(
            contact_body['address']['email'])
        if contactByEmail is not None:
            if contactByEmail.customer_number != contact.customer_number:
                raise EmailExist
        # set birthday, because it immutable
        contact_body['birthday'] = contact.infos['birthday']

        return self.buildContractOutputDto(self.contacts_repository.update_contact(
            Contacts(
                infos=contact_body,
                updated_at=datetime.now().replace(microsecond=0),
                created_at=contact.created_at,
                deleted_at=contact.deleted_at,
                is_activated=contact.is_activated,
                id=contact.id,
                customer_number=contact.customer_number,
            )
        ))

    def delete_contact(self, number: str) -> None:
        contact = self.contacts_repository.get_contact_by_number(number)
        if contact is None:
            raise ContactNotFound
        contact.is_activated = False
        contact.deleted_at = datetime.now().replace(microsecond=0)
        self.contacts_repository.delete_contact(
            contact
        )

    def buildContactOutputDtoWithPagination(
        self, contacts: List[ContactOutputDto], 
        offset: int, 
        limit: int,
        type_contact: SearchAllContact
    ):
        offset: int
        limit: int
        return ContactDtoWithPagination(
            count=self.contacts_repository.count_contact(type_contact),
            total=len(contacts),
            offset=offset,
            limit=limit,
            data=contacts
        )

    def get_contact_by_id_for_admin(self, id: int) -> ContactOutputDto:
        c: Contacts = self.contacts_repository.get_contact_by_id_for_admin(id)
        if c is None:
            raise ContactNotFound
        return self.buildContractOutputDto(c)

    def get_contact_by_pid_for_admin(self, pid: str) -> ContactOutputDto:
        c = self.contacts_repository.get_contact_by_pid_for_admin(pid)
        if c is not None:
            return self.buildContractOutputDto(c)
        else:
            raise ContactNotFound

    def get_contact_by_pid_for_client(self, pid: str) -> ContactOutputDto:
        c = self.contacts_repository.get_contact_by_pid_for_client(pid)
        if c is not None:
            return self.buildContractOutputDto(c)
        else:
            raise ContactNotFound

    def get_contacts_for_admin(self, page: int) -> ContactDtoWithPagination:
        contacts: List[Contacts] = self.contacts_repository.get_contacts_for_admin()
        if len(contacts) != 0:
            return self.buildContactOutputDtoWithPagination([self.buildContractOutputDto(c) for c in contacts], page)
        else:
            raise ContactNotFound

    def get_contacts_for_client(self, offset: int, limit: int,
                                type_contact: SearchAllContact) -> ContactDtoWithPagination:
        contacts: List[Contacts] = self.contacts_repository.get_contacts_for_client(offset, limit, type_contact)
        if len(contacts) != 0:
            return self.buildContactOutputDtoWithPagination(
                [self.buildContractOutputDto(c) for c in contacts],
                offset,
                limit,
                type_contact
            )
        else:
            raise ContactNotFound

    def get_contact_by_email_for_admin(self, email: str) -> ContactOutputDto:
        c = self.contacts_repository.get_contact_by_email_for_admin(email)
        if c is not None:
            return self.buildContractOutputDto(c)
        else:
            raise EmailExist

    def get_contact_by_email_for_client(self, email: str) -> ContactOutputDto:
        c = self.contacts_repository.get_contact_by_email_for_client(email)
        if c is not None:
            return self.buildContractOutputDto(c)
        else:
            raise ContactNotFound

    def get_contact_by_phone_for_admin(self, telephone: str) -> ContactOutputDto:
        # logging.error(f" phone format %s ", self.phoneNumberFormat(telephone))
        c = self.contacts_repository.get_contact_by_phone_for_admin(self.phoneNumberFormat(telephone))
        if c is not None:
            return self.buildContractOutputDto(c)
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
            return self.buildContractOutputDto(c)
        else:
            raise ContactNotFound

    def phoneNumberFormat(self, phoneNumber: str) -> String:
        if phoneNumber.startswith("+224") and not re.compile("^\+224-\d{3}-\d{2}-\d{2}-\d{2}$").match(phoneNumber):
            phoneNumber = phoneNumber[:4] + "-" + phoneNumber[4:7] + "-" + phoneNumber[7:9] + "-" + phoneNumber[9:11] + "-" + phoneNumber[11:13]
        if not phoneNumber.startswith("+224") and not re.compile("^\+224-\d{3}-\d{2}-\d{2}-\d{2}$").match(phoneNumber):
            phoneNumber = "+224-" + phoneNumber[:3] + "-" + phoneNumber[3:5] + "-" + phoneNumber[5:7] + "-" + phoneNumber[7:9]

        return phoneNumber

    def get_contact_by_uid_for_client(self, contact_uid: str) -> ContactOutputDto:
        c = self.contacts_repository.get_contact_by_uid_for_client(contact_uid)
        if c is None:
            raise ContactNotFound
        return self.buildContractOutputDto(c)

    def get_contact_by_uid_for_admin(self, contact_uid: str) -> ContactOutputDto:
        c = self.contacts_repository.get_contact_by_uid_for_admin(contact_uid)
        if c is None:
            raise ContactNotFound
        return self.buildContractOutputDto(c)

    def get_contact_by_id_for_client(self, id: int) -> ContactOutputDto:
        c = self.contacts_repository.get_contact_by_id_for_client(id)
        if c is None:
            raise ContactNotFound("with the id " + str(id))
        return self.buildContractOutputDto(c)

    def get_contact_by_type_for_admin(self, contact_type: str, offset: int, limit: int) -> List[ContactOutputDto]:
        contacts: List[Contacts] = self.contacts_repository.get_contact_by_type_for_admin(contact_type, offset, limit)
        if len(contacts) == 0:
            raise ContactNotFound
        return [self.buildContractOutputDto(c) for c in contacts]

    def get_contact_by_type_for_client(self, contact_type: str, offset: int, limit: int) -> List[ContactOutputDto]:
        contacts: List[Contacts] = self.contacts_repository.get_contact_by_type_for_client(contact_type, offset, limit)
        if len(contacts) == 0:
            raise ContactNotFound
        return [self.buildContractOutputDto(c) for c in contacts]

    def buildContractOutputDto(self, contact: Contacts):
        return ContactOutputDto(
            id=contact.id,
            infos=contact.infos,
            is_activated=contact.is_activated,
            customer_number=contact.customer_number,
            created_at=contact.created_at,
            updated_at=contact.updated_at,
            deleted_at=contact.deleted_at
        )

    def search_contact_by_param(self, query_params: SearchByParams) -> ContactOutputDto:
        if (query_params.phone is None and query_params.email is None and query_params.pid
                is None and query_params.customer_number is None):
            raise SearchParamError
        contact = self.contacts_repository.search_contact_by_param(query_params)
        if contact is None:
            raise ContactNotFound
        return self.buildContractOutputDto(contact)
