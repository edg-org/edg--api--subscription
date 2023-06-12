import json
import logging
from typing import List
from unittest import TestCase
from unittest.mock import create_autospec, patch, Mock
from api.subscriber.models.ContactModel import Contact
from api.subscriber.repositories import ContactRepository
from api.subscriber.schemas.ContactSchema import ContactInfos
from api.subscriber.services.ContactService import ContactService


class TestContactService(TestCase):
    contact_repository: ContactRepository
    contact_service: ContactService

    def setUp(self) -> None:
        super().setUp()

        self.contact_repository = create_autospec(ContactRepository)
        self.contact_service = ContactService(self.contact_repository)
        self.contact_repository.get_contact_by_phone_for_client = Mock()
        self.contact_repository.get_contact_by_email_for_client = Mock()
        self.contact_repository.get_contact_by_pid_for_client = Mock()
        self.contact_repository.get_contact_by_phone_for_admin = Mock()
        self.contact_repository.get_contact_by_email_for_admin = Mock()
        self.contact_repository.get_contact_by_pid_for_admin = Mock()
        self.contact_repository.get_contact_by_type_for_client = Mock()
        self.contact_repository.get_contact_by_type_for_admin = Mock()

    @patch("api.subscriber.schemas.ContactSchema.ContactInfos", autospec=True)
    @patch("api.subscriber.schemas.ContactSchema.ContactInputDto", autospec=True)
    def test_create_contact(self, ContactInfos, ContactInputDto):
        contactInfos: ContactInfos() = self.loadJson()

        self.contact_repository.get_contact_by_phone_for_client.return_value = None
        self.contact_repository.get_contact_by_email_for_client.return_value = None
        self.contact_repository.get_contact_by_pid_for_client.return_value = None

        contactSchema = ContactInputDto()
        contactSchema.infos = contactInfos
        logging.error("contact info type %s ", type(contactInfos))

        self.contact_service.create_contact = Mock()

        self.contact_service.create_contact(contactBody=contactSchema)

        self.contact_repository.create_contact = Mock(return_value=None)

        self.contact_service.create_contact.assert_called_once_with(contactBody=contactSchema)

    def loadJson(self):
        f = open("api/__tests__/createContact.json")
        return json.load(f)

    @patch(
        "api.subscriber.schemas.ContactSchema.ContactInputDto",
        autospec=True,
    )
    def test_update_contact(self, ContactInputDto):
        contactInfos: ContactInfos() = self.loadJson()

        self.contact_repository.get_contact_by_phone_for_client.return_value = None
        self.contact_repository.get_contact_by_email_for_client.return_value = None
        self.contact_repository.get_contact_by_pid_for_client.return_value = None

        contactSchema = ContactInputDto()
        contactSchema.infos = contactInfos
        logging.error("contact info type %s ", type(contactInfos))

        self.contact_service.update_contact = Mock()

        self.contact_service.update_contact("string", contactSchema)

        self.contact_service.update_contact.assert_called_once_with("string", contactSchema)

    def test_get_contact_by_email_for_client(self):
        self.contact_service.buildContractOutputDto = Mock(return_value=None)
        c = self.contact_service.get_contact_by_email_for_client("user@example.com")
        self.contact_repository.get_contact_by_email_for_client.assert_called_once()

    @patch("api.subscriber.schemas.ContactSchema.ContactOutputDto", autospec=True)
    def test_get_contact_by_phone_for_client(self, ContactOutputDto):
        self.contact_service.buildContractOutputDto = Mock(return_value=None)
        self.contact_service.get_contact_by_phone_for_client("+224-610-18-59-36")
        self.contact_repository.get_contact_by_phone_for_client.assert_called_once()


    def test_get_contact_by_pid_for_client(self):
        self.contact_service.buildContractOutputDto = Mock(return_value=None)
        self.contact_service.get_contact_by_pid_for_client("string")
        self.contact_repository.get_contact_by_pid_for_client.assert_called_once()

    def test_get_contact_by_email_for_admin(self):
        self.contact_service.buildContractOutputDto = Mock(return_value=None)
        c = self.contact_service.get_contact_by_email_for_admin("user@example.com")
        self.contact_repository.get_contact_by_email_for_admin.assert_called_once_with("user@example.com")

    def test_get_contact_by_phone_for_admin(self):
        self.contact_service.buildContractOutputDto = Mock(return_value=None)
        self.contact_service.get_contact_by_phone_for_admin("+224-610-18-59-36")
        self.contact_repository.get_contact_by_phone_for_admin.assert_called_once()

    def test_get_contact_by_pid_for_admin(self):
        self.contact_service.buildContractOutputDto = Mock(return_value=None)
        self.contact_service.get_contact_by_pid_for_admin("string")
        self.contact_repository.get_contact_by_pid_for_admin.assert_called_once()

    def test_get_contact_by_type_for_admin(self):
        self.contact_service.buildContractOutputDto = Mock(return_value=None)
        self.contact_repository.get_contact_by_type_for_admin = Mock(return_value=[Contact])
        self.contact_service.get_contact_by_type_for_admin("Client", 0, 4)
        self.contact_repository.get_contact_by_type_for_admin.assert_called_once()

    def test_get_contact_by_type_for_client(self):
        self.contact_service.buildContractOutputDto = Mock(return_value=None)
        self.contact_repository.get_contact_by_type_for_client = Mock(return_value=[Contact])
        self.contact_service.get_contact_by_type_for_client("Client", 0, 4)
        self.contact_repository.get_contact_by_type_for_client.assert_called_once()