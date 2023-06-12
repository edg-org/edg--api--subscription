import json
import logging
from unittest import TestCase
from unittest.mock import create_autospec, patch

from sqlalchemy.orm import Session

from api.subscription.repositories.ContractRepository import ContractRepository
from api.utilis.GuidGenerator import GuidGenerator


class TestSubscriberRepository(TestCase):
    session: Session
    contract_repository: ContractRepository

    def setUp(self):
        super().setUp()
        self.session = create_autospec(Session)
        self.contract_repository = ContractRepository(
            self.session
        )

    @patch("api.subscription.models.ContractModel.Contract", autospec=True)
    def test_create_contract(self, Contract):
        contract_schema = self.loadJson()
        logging.warning(f"mess %s ", type(contract_schema))
        contract = Contract(
            infos=contract_schema[0]['infos'],
            customer_id=contract_schema[0]['customer_id'],
            contract_uid=GuidGenerator.contractUID("O0365412"),
        )
        self.contract_repository.create_contract(contract)

        self.session.add_all.assert_called_once_with(contract)

    @patch("api.subscription.models.ContractModel.Contract", autospec=True)
    def test_update_contract(self, Contract):
        contract_schema = self.loadJson()
        contract = Contract(
            infos=contract_schema[0]['infos'],
            customer_id=contract_schema[0]['customer_id'],
            contract_uid=GuidGenerator.contractUID("O0365412"),
        )

        self.contract_repository.update_contract(contract)

        self.session.merge.assert_called_once_with(contract)

    @patch("api.subscription.models.ContractModel.Contract", autospec=True)
    def test_delete_contract(self, Contract):
        contract_schema = self.loadJson()
        contract = Contract(
            infos=contract_schema[0]['infos'],
            customer_id=contract_schema[0]['customer_id'],
            contract_uid=GuidGenerator.contractUID("O0365412"),
        )

        self.contract_repository.delete_contract(contract)

        self.session.merge.assert_called_once()


    def loadJson(self):
        f = open("api/subscription/__test__/create_contract.json")
        a = json.load(f)
        f.close()
        return a