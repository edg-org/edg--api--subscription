import json
import logging
from unittest import TestCase
from unittest.mock import create_autospec, patch, Mock

from sqlalchemy.orm import Session

from api.services.ContactsService import ContactsService
from subscriber_api.repositories.SubscriberContractRepository import SubscriberContractRepository
from subscriber_api.schemas.SubscriberContractSchema import ContractDtoIncoming
from subscriber_api.services.GuidGenerator import GuidGenerator


class TestSubscriberRepository(TestCase):
    session: Session
    contract_repository: SubscriberContractRepository

    def setUp(self):
        super().setUp()
        self.session = create_autospec(Session)
        self.contract_repository = SubscriberContractRepository(
            self.session
        )

    @patch("subscriber_api.models.SubscriberContractModel.SubscriberContract", autospec=True)
    def test_create_contract(self, SubscriberContract):
        contract_schema = self.loadJson()
        logging.warning(f"mess %s ", type(contract_schema))
        contract = SubscriberContract(
            infos=contract_schema[0]['infos'],
            customer_id=contract_schema[0]['customer_id'],
            contract_uid=GuidGenerator.contractUID("O0365412"),
        )
        self.contract_repository.create_contract(contract)

        self.session.add_all.assert_called_once_with(contract)

    @patch("subscriber_api.models.SubscriberContractModel.SubscriberContract", autospec=True)
    def test_update_contract(self, SubscriberContract):
        contract_schema = self.loadJson()
        contract = SubscriberContract(
            infos=contract_schema[0]['infos'],
            customer_id=contract_schema[0]['customer_id'],
            contract_uid=GuidGenerator.contractUID("O0365412"),
        )

        self.contract_repository.update_contract(contract)

        self.session.merge.assert_called_once_with(contract)

    @patch("subscriber_api.models.SubscriberContractModel.SubscriberContract", autospec=True)
    def test_delete_contract(self, SubscriberContract):
        contract_schema = self.loadJson()
        contract = SubscriberContract(
            infos=contract_schema[0]['infos'],
            customer_id=contract_schema[0]['customer_id'],
            contract_uid=GuidGenerator.contractUID("O0365412"),
        )

        self.contract_repository.delete_contract(contract)

        self.session.merge.assert_called_once()

    def test_get_contract_by_customer_id(self):
        self.contract_repository.get_contract_by_customer_id_for_client(1, 0, 2)
        self.session.scalars.assert_called_once()

    def test_get_contract_by_contract_uid_for_client(self):
        self.contract_repository.get_contract_by_contract_uid_for_client("CFDSGFSDG")
        self.session.scalars.assert_called_once()

    def test_get_contract_by_contact_uid_and_contract_uid_for_client(self):
        self.contract_repository.get_contract_by_contact_uid_and_contract_uid_for_client("adsfdsf", "dasdfsf")
        self.session.scalars.assert_called_once()

    def test_get_contract_by_contact_pid_and_contract_uid_for_client(self):
        self.contract_repository.get_contract_by_contact_pid_and_contract_uid_for_client("Sdsffdsg", "dsfdg")
        self.session.scalars.assert_called_once()

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
        SubscriptionLevelIncomingFilter= Mock()
        SubscriptionLevelIncomingFilter.return_value=None
        AgencyIncomingFilter= Mock()
        AgencyIncomingFilter.return_value=None
        self.contract_repository.get_contract_by_submitted_params(
            ContractDtoIncoming,
            SubscriberContractInfoForFilter,
            AgencyIncomingFilter,
            0,
            2
        )
        self.session.scalars.assert_called_once()

    def loadJson(self):
        f = open("../create_contract.json")
        a = json.load(f)
        f.close()
        return a