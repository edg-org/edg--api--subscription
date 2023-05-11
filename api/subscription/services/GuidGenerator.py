import hashlib
import json
import logging
import string
import uuid
from collections import Counter
from typing import List, Dict

from fastapi import Depends

from api.contact.models.SubscriberContractModel import SubscriberContract
from api.contact.services.ContactsService import ContactsService
from api.subscription.repositories.SubscriberContractRepository import SubscriberContractRepository
from api.subscription.schemas.SubscriberContractSchema import SubscriberContractSchema
from fastapi.encoders import jsonable_encoder


class GuidGenerator:
    subscriber_contract_repository: SubscriberContractRepository
    contact_service: ContactsService

    def __init__(self,
                 subscriber_contract_repository: SubscriberContractRepository = Depends(),
                 contact_service: ContactsService = Depends()
                 ):
        self.subscriber_contract_repository = subscriber_contract_repository
        self.contact_service = contact_service

    def contractUID(self, contact, contract_schemas: List[SubscriberContractSchema]) \
            -> str:
        # get contact from db if exist
        amount_contract = 0
        if contact is not None:
            amount_contract = self.subscriber_contract_repository.count_contract_by_contact_number(
                contact.customer_number)
        # check for repeating contract for given customer id in contract_schemas variable
        contract_schemas = json.dumps([contract.dict() for contract in contract_schemas])
        contract_schemas = json.loads(contract_schemas)
        customer_count = Counter(item['customer_id'] for item in contract_schemas)
        customer_repeat = dict()
        value_to_return = []
        for i, (customer, count) in enumerate(customer_count.items()):
            customer_repeat['customer_id'] = customer
            customer_repeat['count'] = count
        logging.warning(customer_repeat)

        return "C" + str(abs(hash(contact.infos['identity']['pid'])) % (10 ** 7))
