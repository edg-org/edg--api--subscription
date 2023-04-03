import json
import logging
from unittest import TestCase
from unittest.mock import create_autospec, patch, Mock, MagicMock

from api.repositories import ContactsRepository
from api.schemas.pydantic.ContactsSchema import ContactsSchema, ContactInfos
from api.services.ContactsService import ContactsService


class TestContactService(TestCase):
    contact_repository: ContactsRepository
    contact_service: ContactsService

    def setUp(self) -> None:
        super().setUp()

        self.contact_repository = create_autospec(
            ContactsRepository
        )
        self.contact_service = ContactsService(
            self.contact_repository
        )
        self.contact_repository.get_contact_by_phone_for_client = Mock()
        self.contact_repository.get_contact_by_email_for_client = Mock()
        self.contact_repository.get_contact_by_pid_for_client = Mock()
        self.contact_repository.get_contact_by_phone_for_admin = Mock()
        self.contact_repository.get_contact_by_email_for_admin = Mock()
        self.contact_repository.get_contact_by_pid_for_admin = Mock()

    @patch("api.schemas.pydantic.ContactsSchema.ContactInfos", autospec=True)
    @patch("api.schemas.pydantic.ContactsSchema.ContactsSchema", autospec=True)
    def test_create_contact(self, ContactInfos, ContactsSchema):
        contactInfos: ContactInfos() = self.loadJson()

        self.contact_repository.get_contact_by_phone_for_client.return_value = None
        self.contact_repository.get_contact_by_email_for_client.return_value = None
        self.contact_repository.get_contact_by_pid_for_client.return_value = None

        contactSchema = ContactsSchema()
        contactSchema.infos = contactInfos
        logging.error("contact info type %s ", type(contactInfos))

        self.contact_service.create_contact = Mock()

        self.contact_service.create_contact(contactBody=contactSchema)

        self.contact_repository.create_contact = Mock(return_value=None)

        self.contact_service.create_contact.assert_called_once_with(contactBody=contactSchema)

        # self.contactRepository.createContact.assert_called_once()

    def loadJson(self):
        f = open("../createContactService.json")
        return json.load(f)

    @patch(
        "api.schemas.pydantic.ContactsSchema.ContactsSchema",
        autospec=True,
    )
    def test_update_contact(self, ContactsSchema):
        contactInfos: ContactInfos() = self.loadJson()

        self.contact_repository.get_contact_by_phone_for_client.return_value = None
        self.contact_repository.get_contact_by_email_for_client.return_value = None
        self.contact_repository.get_contact_by_pid_for_client.return_value = None

        contactSchema = ContactsSchema()
        contactSchema.infos = contactInfos
        logging.error("contact info type %s ", type(contactInfos))

        self.contact_service.update_contact = Mock()

        self.contact_service.update_contact("string", contactSchema)

        self.contact_service.update_contact.assert_called_once_with("string", contactSchema)

    def test_get_contact_by_email_for_client(self):
        c = self.contact_service.get_contact_by_email_for_client("user@example.com")
        logging.info(f" result %s ", c.infos)
        self.contact_repository.get_contact_by_email_for_client.assert_called_once_with("user@example.com")

    def test_get_contact_by_phone_for_client(self):
        self.contact_service.get_contact_by_phone_for_client("+224-610-18-59-36")
        self.contact_repository.get_contact_by_phone_for_client.assert_called_once()

    def test_get_contact_by_pid_for_client(self):
        self.contact_service.get_contact_by_pid_for_client("string")
        self.contact_repository.get_contact_by_pid_for_client.assert_called_once()

    def test_get_contact_by_email_for_admin(self):
        c = self.contact_service.get_contact_by_email_for_admin("user@example.com")
        logging.info(f" result %s ", c.infos)
        self.contact_repository.get_contact_by_email_for_admin.assert_called_once_with("user@example.com")

    def test_get_contact_by_phone_for_admin(self):
        self.contact_service.get_contact_by_phone_for_admin("+224-610-18-59-36")
        self.contact_repository.get_contact_by_phone_for_admin.assert_called_once()

    def test_get_contact_by_pid_for_admin(self):
        self.contact_service.get_contact_by_pid_for_admin("string")
        self.contact_repository.get_contact_by_pid_for_admin.assert_called_once()
