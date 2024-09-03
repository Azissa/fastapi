from pydantic import BaseModel
from typing import List,Optional

class StudentBase(BaseModel):
    name: str
    school_id: int

class StudentCreate(StudentBase):
    pass

class StudentUpdate(StudentBase):
    pass
    updated_rows: Optional[int] = None

class StudentRequest(StudentBase):
    pass

class StudentResponse(StudentBase):
    id: int

    class Config:
        orm_mode = True

class StudentWithSchoolResponse(BaseModel):
    id: int
    name: str
    school_id: int
    school_name: str    


class SchoolBase(BaseModel): 
    name: str

class SchoolCreate(SchoolBase):
    pass

class SchoolUpdate(SchoolBase):
    pass

class SchoolRequest(SchoolBase):
    pass

class SchoolResponse(SchoolBase):
    id: int

    class Config:
        orm_mode = True

class SchoolWithStudent(BaseModel):
    id: int
    name: str
    students: List[StudentResponse]
    
    
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []
    
class User(BaseModel):
    username: str
    email: str | None = None
    fullname: str | None = None
    disabled: str | None = None
    
class UserInDB(User):
    hashed_password: str

