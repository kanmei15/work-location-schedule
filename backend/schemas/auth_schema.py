from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginResponse(BaseModel):
    message: str
    csrf_token: str
    is_default_password: bool
    
class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str