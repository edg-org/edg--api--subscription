from api.utilis.Helper import Helper
from api.configs.Environment import get_env_var
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

env = get_env_var()

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        authorization = request.headers.get("Authorization")
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authentication scheme.")
            return await Helper.generic_request_query(f"{env.auth_domain_name}/v1/token/introspect", authorization)

        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid authorization code.")
