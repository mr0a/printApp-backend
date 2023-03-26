import json

from fastapi import Request, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from typing import Union, Tuple
from jose import jwt
from starlette.authentication import AuthenticationBackend, AuthenticationError, AuthCredentials, BaseUser, SimpleUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class JWTUser(SimpleUser):

    @property
    def identity(self) -> str:
        return self.username

    def __init__(self, user_id: int, username: str, token: str, payload: dict) -> None:
        self.username = username
        self.token = token
        self.payload = payload
        self.id = user_id


class JWTAuthenticationBackend(AuthenticationBackend):
    def __init__(self,
                 secret_key: str,
                 algorithm: str = 'HS256',
                 prefix: str = 'JWT',
                 username_field: str = 'sub',
                 ) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.prefix = prefix
        self.username_field = username_field

    @classmethod
    def get_token_from_header(cls, authorization: str, prefix: str) -> str:
        """Parses the Authorization header and returns only the token"""
        try:
            scheme, token = authorization.split()
        except ValueError:
            raise AuthenticationError('Could not separate Authorization scheme and token')
        if scheme.lower() != prefix.lower():
            raise AuthenticationError(f'Authorization scheme {scheme} is not supported')
        return token

    async def authenticate(self, request) -> Union[None, Tuple[AuthCredentials, BaseUser]]:
        if "Authorization" not in request.headers:
            return None

        auth = request.headers["Authorization"]
        token = self.get_token_from_header(authorization=auth, prefix=self.prefix)
        try:
            payload = jwt.decode(token, key=self.secret_key, algorithms=self.algorithm)
        except jwt.JWTError as e:
            raise AuthenticationError(str(e))
        subject = json.loads(payload[self.username_field])
        return AuthCredentials(["authenticated"]), JWTUser(
            username=subject["username"], user_id=subject["user_id"], token=token, payload=payload)


async def authentication_required(request: Request, token: str = Depends(oauth2_scheme)):
    # It Depends on oauth2_scheme to add the login form in swagger
    if request.user:
        if not request.user.is_authenticated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Login to access the resource."
            )
