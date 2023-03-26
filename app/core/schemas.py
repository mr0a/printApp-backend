from pydantic import BaseModel


class LoginResponse(BaseModel):
    username: str
    credits: int
    access_token: str
    token_type: str

