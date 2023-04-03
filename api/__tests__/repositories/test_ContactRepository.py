import json
from datetime import datetime
from unittest import TestCase
from unittest.mock import create_autospec, Mock, patch

from sqlalchemy.orm import Session

from api.repositories.ContactsRepository import ContactsRepository


class TestContactRepository(TestCase):
    session: Session
    contacts_repository: ContactsRepository

    def setUp(self):
        super().setUp()
        self.session = create_autospec(Session)
        self.contacts_repository = ContactsRepository(
            self.session
        )

    @patch("api.models.ContactsModel.Contacts", autospec=True)
    def test_create_contact(self, Contacts):
        contact = Contacts(infos=self.loadJson())

        self.contacts_repository.create_contact(contact)

        self.session.add.assert_called_once_with(contact)

    @patch("api.models.ContactsModel.Contacts", autospec=True)
    def test_update_contact(self, Contacts):
        contact = Contacts(infos=self.loadJson())

        self.contacts_repository.update_contact(contact)

        self.session.merge.assert_called_once_with(contact)

    def test_delete_contact(self):
        self.contacts_repository.delete_contact("stringOP")

        self.session.merge.assert_called_once()

    def test_get_contact_by_pid_for_admin(self):
        self.contacts_repository.get_contact_by_pid_for_admin("stringOPkop")

        self.session.scalars.assert_called_once()

    def test_get_contact_by_email_for_admin(self):
        self.contacts_repository.get_contact_by_email_for_admin("userop3@example.com")
        self.session.scalars.assert_called_once()

    def test_get_contact_by_phone_for_admin(self):
        self.contacts_repository.get_contact_by_phone_for_admin("+224-610-18-22-15")
        self.session.scalars.assert_called_once()

    def test_get_contacts_for_admin(self):
        self.contacts_repository.get_contacts_for_admin(0, 4)
        self.session.scalars.assert_called_once()

    def test_get_contact_by_pid_for_client(self):
        self.contacts_repository.get_contact_by_pid_for_client("stringOPkop")

        self.session.scalars.assert_called_once()

    def test_get_contact_by_email_for_client(self):
        self.contacts_repository.get_contact_by_email_for_client("userop3@example.com")
        self.session.scalars.assert_called_once()

    def test_get_contact_by_phone_for_client(self):
        self.contacts_repository.get_contact_by_phone_for_client("+224-610-18-22-15")
        self.session.scalars.assert_called_once()

    def test_get_contacts_for_client(self):
        self.contacts_repository.get_contacts_for_client(0, 4)
        self.session.scalars.assert_called_once()

    def loadJson(self):
        f = open("../createContact.json")
        return json.load(f)