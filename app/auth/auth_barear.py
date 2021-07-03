from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .auth_handler import decodeJWT


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)
        self.obrigatorio = auto_error

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            decoded_jwt = self.verify_jwt(credentials.credentials)
            if not decoded_jwt:
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return decoded_jwt
        elif self.obrigatorio:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")
        else:
            None

    def verify_jwt(self, jwtoken: str) -> str:
        try:
            payload = decodeJWT(jwtoken)
            payload['access_token'] = jwtoken
        except:
            payload = None
        return payload
