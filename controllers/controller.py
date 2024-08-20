from fastapi import APIRouter
from typing import List
from schemas.schemas import SchoolCreate, SchoolUpdate, SchoolResponse, StudentCreate, StudentUpdate, StudentResponse
from services.service import SchoolService, StudentService
router = APIRouter()
school_service = SchoolService()
student_service = StudentService()

# School Endpoints
@router.get("/schools/", response_model=List[SchoolResponse])
def list_schools():
    return school_service.list_schools()

@router.get("/schools/{school_id}", response_model=SchoolResponse)
def show_school(school_id: int):
    return school_service.show_school(school_id)

@router.post("/schools/", response_model=SchoolResponse)
def create_school(school: SchoolCreate):
    return school_service.create_school(school)

@router.put("/schools/{school_id}", response_model=SchoolResponse)
def update_school(school_id: int, school: SchoolUpdate):
    return school_service.update_school(school_id, school)

@router.delete("/schools/{school_id}")
def delete_school(school_id: int):
    school_service.delete_school(school_id)
    return {"detail": "School deleted"}

# Student Endpoints
@router.get("/students/", response_model=List[StudentResponse])
def list_students():
    return student_service.list_students()

@router.get("/students/{student_id}", response_model=StudentResponse)
def show_student(student_id: int):
    return student_service.show_student(student_id)

@router.post("/students/", response_model=StudentResponse)
def create_student(student: StudentCreate):
    return student_service.create_student(student)

@router.put("/students/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student: StudentUpdate):
    return student_service.update_student(student_id, student)

@router.delete("/students/{student_id}")
def delete_student(student_id: int):
    student_service.delete_student(student_id)
    return {"detail": "Student deleted"}

@router.get("/students/multiply/{student_id}" ,response_model=StudentResponse)
def multiply(student_id: int):
    return student_service.multiply(student_id)