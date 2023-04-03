import json
import logging
import re
from datetime import datetime, date
from typing import List, Optional

from fastapi import Depends, HTTPException
from sqlalchemy import String, Result, Row

from api.models.ContactsModel import Contacts
from api.repositories.ContactsRepository import ContactsRepository
from api.schemas.pydantic.ContactsSchema import ContactsSchema, ContactInfos
from api.services.GuidGenerator import GuidGenerator


class ContactsService:
    contacts_repository: ContactsRepository

    def __init__(self, contacts_repository: ContactsRepository = Depends()) -> None:
        self.contacts_repository = contacts_repository

    def create_contact(self, contact_body: ContactsSchema) -> Contacts:
        # Convertissons notre object en json
        contact_body.infos = json.loads(contact_body.infos.json())
        '''
            Pour ne pas ajouter deux utilisateur avec utilisant le meme numero
            email et la carte d'identite nous procedons a la verification dans la base 
            de donne et retournons un message d'erreur au cas ou les donnees sont deja 
            retrouvees dans la bd
        '''
        if self.contacts_repository.get_contact_by_phone_for_client(
                contact_body.infos['address']['telephone']) is not None:
            raise HTTPException(status_code=400, detail="This phone number is already used by another user, please "
                                                        "provide an other")
        if self.contacts_repository.get_contact_by_email_for_client(contact_body.infos['address']['email']) is not None:
            raise HTTPException(status_code=400, detail="This email is already used by another user, please provide "
                                                        "an other")
        if self.contacts_repository.get_contact_by_pid_for_client(contact_body.infos['identity']['pid']) is not \
                None:
            raise HTTPException(status_code=400, detail="This pid is already used by another user, please provide an "
                                                        "other")

        return self.contacts_repository.create_contact(
            Contacts(
                infos=contact_body.infos,
                contact_uid=GuidGenerator.contactUID(contact_body.infos['identity']['pid']),
                created_at=date.today()
            )
        )

    def update_contact(self, pid: str, contact_body: ContactsSchema) -> Contacts:
        # Convertissons notre object en json
        contact_body.infos = json.loads(contact_body.infos.json())
        '''
            La modification est effectuer par le numero d'identifiant unique (passport ou carte d'identite) 
            pour ce fait nous verifions l'existance de l'utilisateur dans la bd, au cas ou il n'existe pas 
            on retourne une erreur 403
        '''
        contact: Contacts = self.contacts_repository.get_contact_by_pid_for_client(pid)
        checkIdentity: Contacts = self.contacts_repository.get_contact_by_pid_for_client(
            contact_body.infos['identity']['pid'])
        if contact is None:
            raise HTTPException(status_code=400, detail="The user you trying to update does not exist, the operation "
                                                        "cannot be achieved")
        if checkIdentity is not None:
            if checkIdentity.infos['identity']['pid'] != pid:
                raise HTTPException(status_code=400, detail="The submitted pid is already used by another user, please "
                                                        "provide a correct one")
        # Pendant la modification nous verifions si le numero modifie n'existe pas dans la bd
        contactByPhone: Contacts = self.contacts_repository.get_contact_by_phone_for_client(
            contact_body.infos['address']['telephone'])
        if contactByPhone is not None:
            if contactByPhone.contact_uid != contact.contact_uid:
                raise HTTPException(status_code=400, detail="This phone number is already used by another user, "
                                                            "please provide an other")

        # Pendant la modification nous verifions si l'email modifie n'existe pas dans la bd
        contactByEmail: Contacts = self.contacts_repository.get_contact_by_email_for_client(
            contact_body.infos['address']['email'])
        if contactByEmail is not None:
            if contactByEmail.contact_uid != contact.contact_uid:
                raise HTTPException(status_code=400, detail="This email is already used by another user, please "
                                                            "provide an other")

        return self.contacts_repository.update_contact(
            Contacts(
                infos=contact_body.infos,
                updated_at=date.today(),
                created_at=contact.created_at,
                deleted_at=contact.deleted_at,
                is_deleted=contact.is_deleted,
                id=contact.id,
                contact_uid=contact.contact_uid,
            )
        )

    def delete_contact(self, pid: str) -> None:
        contact = self.contacts_repository.get_contact_by_pid_for_client(pid)
        if contact is None:
            raise HTTPException(status_code=404, detail="The user pid is does not exist, the operation cannot be "
                                                        "achieved")
        contact.is_deleted = True
        contact.deleted_at = date.today()
        self.contacts_repository.delete_contact(
            contact
        )

    def get_contact_by_id_for_admin(self, id: int) -> Optional[Contacts]:
        return self.contacts_repository.get_contact_by_id_for_admin(
            id
        )

    def get_contact_by_pid_for_admin(self, pid: str) -> Contacts:
        c = self.contacts_repository.get_contact_by_pid_for_admin(pid)
        if c is not None:
            return c
        else:
            raise HTTPException(status_code=404, detail="We didn't found user with the submitted pid")

    def get_contact_by_pid_for_client(self, pid: str) -> Contacts:
        c = self.contacts_repository.get_contact_by_pid_for_client(pid)
        if c is not None:
            return c
        else:
            raise HTTPException(status_code=404, detail="We didn't found user with the submitted pid")

    def get_contacts_for_admin(self, offset: int, limit: int) -> Contacts:
        c = self.contacts_repository.get_contacts_for_admin(offset, limit)
        if c is not None:
            return c
        else:
            raise HTTPException(status_code=404, detail="We didn't found any user")

    def get_contacts_for_client(self, offset: int, limit: int) -> Contacts:
        c = self.contacts_repository.get_contacts_for_client(offset, limit)
        if c is not None:
            return c
        else:
            raise HTTPException(status_code=404, detail="We didn't found any user")

    def get_contact_by_email_for_admin(self, email: str) -> Contacts:
        c = self.contacts_repository.get_contact_by_email_for_admin(email)
        if c is not None:
            return c
        else:
            raise HTTPException(status_code=404, detail="we didn't found any user with this email , please make sure "
                                                        "that you provide a correct email ")

    def get_contact_by_email_for_client(self, email: str) -> Contacts:
        c = self.contacts_repository.get_contact_by_email_for_client(email)
        if c is not None:
            return c
        else:
            raise HTTPException(status_code=404, detail="we didn't found any user with this email , please make sure "
                                                        "that you provide a correct email ")

    def get_contact_by_phone_for_admin(self, telephone: str) -> Contacts:
        # logging.error(f" phone format %s ", self.phoneNumberFormat(telephone))
        c = self.contacts_repository.get_contact_by_phone_for_admin(self.phoneNumberFormat(telephone))
        if c is not None:
            return c
        else:
            raise HTTPException(status_code=404, detail="we didn't found any user with this phone number , please "
                                                        "make sure that you provide a correct phone number")

    """ Cette fonction nous permet de formater le numero de telephone au format
        Guineen +224-610-15-96-20, pour etre utilise pour les fins de comparaison avec 
        celle de la bd
       """

    def get_contact_by_phone_for_client(self, telephone: str) -> Contacts:
        # logging.error(f" phone format %s ", self.phoneNumberFormat(telephone))
        c = self.contacts_repository.get_contact_by_phone_for_client(self.phoneNumberFormat(telephone))
        if c is not None:
            return c
        else:
            raise HTTPException(status_code=404, detail="we didn't found any user with this phone number , please "
                                                        "make sure that you provide a correct phone number")

    def phoneNumberFormat(self, phoneNumber: str) -> String:
        if phoneNumber.startswith("+224") and not re.compile("^\+224-\d{3}-\d{2}-\d{2}-\d{2}$").match(phoneNumber):
            phoneNumber = phoneNumber[:4] + "-" + phoneNumber[4:7] + "-" + phoneNumber[7:9] + "-" + phoneNumber[9:11] \
                          + "-" + phoneNumber[11:13]
        if not phoneNumber.startswith("+224") and not re.compile("^\+224-\d{3}-\d{2}-\d{2}-\d{2}$").match(phoneNumber):
            phoneNumber = "+224-" + phoneNumber[:3] + "-" + phoneNumber[3:5] + "-" + phoneNumber[5:7] \
                          + "-" + phoneNumber[7:9]

        return phoneNumber

    def get_contact_by_uid_for_client(self, contact_uid: str) -> Contacts:
        c = self.contacts_repository.get_contact_by_uid_for_client(contact_uid)
        if c is None:
            raise HTTPException(status_code=404, detail="We didn't found any user with the user's ID")
        return c

    def get_contact_by_uid_for_admin(self, contact_uid: str) -> Contacts:
        c = self.contacts_repository.get_contact_by_uid_for_admin(contact_uid)
        if c is None:
            raise HTTPException(status_code=404, detail="We didn't found any user with the user's ID")
        return c

    def get_contact_by_id_for_client(self, id: int) -> Contacts:
        c = self.contacts_repository.get_contact_by_id_for_client(id)
        if c is None:
            raise HTTPException(status_code=404, detail="We didn't found any user with the provided id")
        return c

    def get_contact_by_id_for_admin(self, id: int) -> Contacts:
        c = self.contacts_repository.get_contact_by_id_for_admin(id)
        if c is None:
            raise HTTPException(status_code=404, detail="We didn't found any user with the provided id")
        return c

    def get_contact_by_type_for_admin(self, contact_type: str, offset: int, limit: int) -> List[Contacts]:
        c = self.contacts_repository.get_contact_by_type_for_admin(contact_type, offset, limit)
        if c is None:
            raise HTTPException(status_code=404, detail="We didn't found any user with the provided contact type")
        return c

    def get_contact_by_type_for_client(self, contact_type: str, offset: int, limit: int) -> List[Contacts]:
        c = self.contacts_repository.get_contact_by_type_for_client(contact_type, offset, limit)
        if c is None:
            raise HTTPException(status_code=404, detail="We didn't found any user with the provided contact type")
        return c
