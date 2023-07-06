from typing import List

from fastapi import Depends, HTTPException
from fastapi.logger import logger

from api.exceptions import RoleBasedAccessError
from api.subscription.schemas.ContractSchema import UserCredential
from api.subscription.utilis.JWTBearer import JWTBearer


class RoleBasedAccess:
    def __init__(self, allowed_roles: List):
        self.allowed_roles = allowed_roles
        print("===============ROLE ALLOWED ==============", self.allowed_roles)

    def __call__(self, user: UserCredential = Depends(JWTBearer())):
        common = set(self.allowed_roles) & set(user.claims.roles)
        if len(common)==0:
            raise RoleBasedAccessError