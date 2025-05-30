from pydantic import BaseModel

class TokenResponseBase(BaseModel):
    access_token: str
    refresh_token: str
    csrf_token: str
    is_default_password: bool

class LambdaLoginResponse(TokenResponseBase):
    message: str