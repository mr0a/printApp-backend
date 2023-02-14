from pydantic import BaseModel


class LoginResponse(BaseModel):
    username: str
    credits: int
    is_repro_admin: bool
    access_token: str
    token_type: str

