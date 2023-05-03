import json
from unittest import TestCase
from unittest.mock import create_autospec, Mock, patch

from api.contact.repositories.ContactsRepository import ContactsRepository
from api.contact.services.ContactsService import ContactsService
from api.subscription.repositories.SubscriberContractRepository import SubscriberContractRepository
from api.subscription.services.SubscriberContractService import SubscriberContactService


def loadJson():
    f = open("api/subscription/__test__/create_contract.json")
    a = json.load(f)
    f.close()
    return a


class SubscriberContractService(TestCase):
    contract_repository: SubscriberContractRepository
    contract_service: SubscriberContactService
    contacts_service: ContactsService
    contacts_repository: ContactsRepository

    def setUp(self) -> None:
        super().setUp()

        self.contract_repository = create_autospec(
            SubscriberContractRepository
        )
        self.contacts_repository = create_autospec(
            ContactsRepository
        )
        self.contract_service = SubscriberContactService(
            self.contract_repository
        )
        self.contacts_service = ContactsService(
            self.contacts_repository
        )
        self.contract_service.check_save_business_logic = Mock(return_value=None)
        self.contract_repository.get_contract_by_delivery_point = Mock(return_value=None)

    @patch("api.subscription.schemas.SubscriberContractSchema.SubscriberContractSchema", autospec=True)
    def test_create_contract(self, SubscriberContractSchema):
        self.contract_repository.create_contract = Mock(return_value=None)
        self.contract_service.buildContractDto = Mock(return_value=None)
        contract_schema = SubscriberContractSchema()
        self.contract_service.create_contract = Mock(return_value=None)
        self.contract_service.create_contract(contract_schema)
        self.contract_service.create_contract.assert_called_once()
        self.contract_repository.create_contract(contract_schema)
        self.contract_repository.create_contract.assert_called_once_with(contract_schema)

    @patch("api.subscription.schemas.SubscriberContractSchema.SubscriberContractSchema", autospec=True)
    def test_update_contract(self, SubscriberContractSchema):
        contract_schema = SubscriberContractSchema()
        self.contract_repository.get_contract_by_contract_uid_for_client = Mock(return_value=None)
        self.contacts_service.get_contact_by_id_for_client = Mock(
            return_value=
            {
                "infos": {
                    "job": "string",
                    "name": "string",
                    "type": "Client",
                    "address": {
                        "email": "user@example.com",
                        "quartier": "string",
                        "telephone": "+224-610-18-22-09"
                    },
                    "birthday": "2000-04-17",
                    "identity": {
                        "pid": "string",
                        "type": "string",
                        "given_date": "2023-04-17",
                        "expire_date": "2023-04-17"
                    },
                    "firstname": "string"
                },
                "is_activated": True,
                "created_at": "2023-04-17",
                "deleted_at": None,
                "id": 1,
                "contact_uid": "CL6392067",
                "updated_at": None
            }
        )

        self.contract_repository.get_contract_by_delivery_point = Mock(return_value=None)
        self.contract_service.update_contract = Mock(return_value=None)
        self.contract_service.update_contract("dsfdg", contract_schema)
        self.contract_service.update_contract.assert_called_once()
        self.contract_repository.update_contract = Mock(return_value=None)
        self.contract_repository.update_contract(contract_schema)
        self.contract_repository.update_contract.assert_called_once_with(contract_schema)

    @patch("api.contact.models.SubscriberContractModel.SubscriberContract", autospec=True)
    def test_delete_contract(self, SubscriberContract):
        contract = SubscriberContract()
        self.contract_service.delete_contract = Mock(return_value=None)
        self.contract_service.delete_contract(contract)
        self.contract_service.delete_contract.assert_called_once()
        self.contract_repository.delete_contract = Mock(return_value=contract)
        self.contract_repository.delete_contract(contract)
        self.contract_repository.delete_contract.assert_called_once_with(contract)

