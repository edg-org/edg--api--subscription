import json
from typing import List
from unittest import TestCase
from unittest.mock import create_autospec, Mock, patch

from sqlalchemy import true

from api.repositories.ContactsRepository import ContactsRepository
from api.services.ContactsService import ContactsService
from api.services.GuidGenerator import GuidGenerator
from subscriber_api.repositories.SubscriberContractRepository import SubscriberContractRepository
from subscriber_api.services import SubscriberContractService
from subscriber_api.services.SubscriberContractService import SubscriberContactService


def loadJson():
    f = open("../create_contract.json")
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

    @patch("subscriber_api.schemas.SubscriberContractSchema.SubscriberContractSchema", autospec=True)
    def test_create_contract(self, SubscriberContractSchema):
        self.contract_repository.create_contract = Mock(return_value=None)
        self.contract_service.buildContractDto = Mock(return_value=None)
        contract_schema = SubscriberContractSchema()
        self.contract_service.create_contract = Mock(return_value=None)
        self.contract_service.create_contract(contract_schema)
        self.contract_service.create_contract.assert_called_once()
        self.contract_repository.create_contract(contract_schema)
        self.contract_repository.create_contract.assert_called_once_with(contract_schema)

    @patch("subscriber_api.schemas.SubscriberContractSchema.SubscriberContractSchema", autospec=True)
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

    @patch("subscriber_api.models.SubscriberContractModel.SubscriberContract", autospec=True)
    def test_delete_contract(self, SubscriberContract):
        contract = SubscriberContract()
        self.contract_service.delete_contract = Mock(return_value=None)
        self.contract_service.delete_contract(contract)
        self.contract_service.delete_contract.assert_called_once()
        self.contract_repository.delete_contract = Mock(return_value=contract)
        self.contract_repository.delete_contract(contract)
        self.contract_repository.delete_contract.assert_called_once_with(contract)

    def test_get_contract_by_customer_id(self):
        self.contract_service.get_contract_by_customer_id_for_client = Mock(return_value=None)
        self.contract_service.get_contract_by_customer_id_for_client(1)
        self.contract_service.get_contract_by_customer_id_for_client.assert_called_once()
        self.contract_repository.get_contract_by_customer_id_for_client = Mock(return_value=None)
        self.contract_repository.get_contract_by_customer_id_for_client(1)
        self.contract_repository.get_contract_by_customer_id_for_client.assert_called_once()

    def test_get_contract_by_contract_uid_for_client(self):
        self.contract_service.get_contract_by_contract_uid_for_client = Mock(return_value=None)
        self.contract_service.get_contract_by_contract_uid_for_client("fdfgdg")
        self.contract_service.get_contract_by_contract_uid_for_client.assert_called_once()
        self.contract_repository.get_contract_by_contract_uid_for_client = Mock(return_value=None)
        self.contract_repository.get_contract_by_contract_uid_for_client("fdfgdg")
        self.contract_repository.get_contract_by_contract_uid_for_client.assert_called_once()

    def test_get_contract_by_contact_uid_and_contract_uid_for_client(self):
        self.contract_service.get_contract_by_contact_uid_and_contract_uid_for_client = Mock(return_value=None)
        self.contract_service.get_contract_by_contact_uid_and_contract_uid_for_client("adsfdsf", "dasdfsf")
        self.contract_service.get_contract_by_contact_uid_and_contract_uid_for_client.assert_called_once()
        self.contract_repository.get_contract_by_contact_uid_and_contract_uid_for_client = Mock(return_value=None)
        self.contract_repository.get_contract_by_contact_uid_and_contract_uid_for_client("adsfdsf", "dasdfsf")
        self.contract_repository.get_contract_by_contact_uid_and_contract_uid_for_client.assert_called_once()

    def test_get_contract_by_contact_pid_and_contract_uid_for_client(self):
        self.contract_service.get_contract_by_contact_pid_and_contract_uid_for_client = Mock(return_value=None)
        self.contract_service.get_contract_by_contact_pid_and_contract_uid_for_client("adsfdsf", "dasdfsf")
        self.contract_service.get_contract_by_contact_pid_and_contract_uid_for_client.assert_called_once()
        self.contract_repository.get_contract_by_contact_pid_and_contract_uid_for_client = Mock(return_value=None)
        self.contract_repository.get_contract_by_contact_pid_and_contract_uid_for_client("adsfdsf", "dasdfsf")
        self.contract_repository.get_contract_by_contact_pid_and_contract_uid_for_client.assert_called_once()

    @patch("subscriber_api.schemas.SubscriberContractSchema.ContractDtoIncoming", autospec=True)
    @patch("subscriber_api.schemas.SubscriberContractSchema.SubscriberContractInfoForFilter", autospec=True)
    @patch("subscriber_api.schemas.SubscriberContractSchema.AgencyIncomingFilter", autospec=True)
    def test_get_contract_by_submitted_params(self,
                                              ContractDtoIncoming,
                                              SubscriberContractInfoForFilter,
                                              AgencyIncomingFilter
                                              ):
        ContractDtoIncoming = Mock()
        ContractDtoIncoming.return_value = None
        SubscriberContractInfoForFilter = Mock()
        SubscriberContractInfoForFilter.return_value = None
        SubscriptionLevelIncomingFilter = Mock()
        SubscriptionLevelIncomingFilter.return_value = None
        AgencyIncomingFilter = Mock()
        AgencyIncomingFilter.return_value = None
        self.contract_service.get_contract_by_submitted_params = Mock(return_value=None)
        self.contract_repository.get_contract_by_submitted_params = Mock(return_value=None)
        self.contract_service.get_contract_by_submitted_params(
            ContractDtoIncoming,
            SubscriberContractInfoForFilter,
            AgencyIncomingFilter,
            0,
            2
        )
        self.contract_service.get_contract_by_submitted_params.assert_called_once()
        self.contract_repository.get_contract_by_submitted_params(
            ContractDtoIncoming,
            SubscriberContractInfoForFilter,
            AgencyIncomingFilter,
            0,
            2
        )
        self.contract_repository.get_contract_by_submitted_params.assert_called_once()