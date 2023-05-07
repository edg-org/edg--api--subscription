import hashlib
import string
import uuid


class GuidGenerator:
    @classmethod
    def contractUID(cls, identityNumber: str) -> str:
        return "C" + str(abs(hash(identityNumber)) % (10 ** 7))