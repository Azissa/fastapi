from pydantic import BaseModel
from typing import List

class StudentBase(BaseModel):
    
    name: str
    school_id: int

class StudentCreate(StudentBase):
    pass

class StudentUpdate(StudentBase):
    pass

class StudentResponse(StudentBase):
    id: int
    name: str
    school_id: int

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

class SchoolResponse(SchoolBase):
    id: int

    class Config:
        orm_mode = True

class SchoolWithStudent(BaseModel):
    id: int
    name: str
    students: List[StudentResponse]

