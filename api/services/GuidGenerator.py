import uuid


class GuidGenerator:

    @classmethod
    def contactUID(cls, identityNumber: str) -> str:
        return "CL"+str(abs(hash(identityNumber)) % (10**7))