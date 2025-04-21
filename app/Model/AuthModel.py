from pydantic import BaseModel

class SignInModel(BaseModel):
    email: str
    password: str
    
class SignUpModel(BaseModel):
    email: str
    password: str
