from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Request, HTTPException

from auth.auth_handler import decodeJWT
from schemas.user_schemas import Role


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if not credentials:
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization code."
            )

        if credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication scheme."
            )

        payload = self.verify_jwt(credentials.credentials)

        if not payload:
            raise HTTPException(
                status_code=403,
                detail="Invalid token, expired token, or insufficient role."
            )

        return payload   # ← return payload instead of token


    def verify_jwt(self, jwtoken: str):
        try:
            payload = decodeJWT(jwtoken)

            if not payload:
                return None

            role = payload.get("role")

            print(role)

            if role not in [Role.ADMIN.value, Role.SUPER_ADMIN.value]:
                return None

            return payload

        except Exception:
            return None