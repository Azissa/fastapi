from typing import List
from models.models import School, Student, schools_db, students_db
from schemas.schemas import SchoolCreate, SchoolUpdate, SchoolResponse, StudentCreate, StudentUpdate, StudentResponse
from exceptions.custom_exceptions import CustomHTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

class StudentService:
    def __init__(self):
        self.students = students_db

    def list_students(self) -> List[Student]:
        return self.students

    def show_student(self, student_id: int) -> Student:
        student = next((student for student in self.students if student.id == student_id), None)
        if student is None:
            raise CustomHTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        return student

    def create_student(self, student: StudentCreate) -> StudentResponse:
        new_id = max((s.id for s in self.students), default=0) + 1
        new_student = Student(id=new_id, name=student.name)
        self.students.append(new_student)
        return StudentResponse.from_orm(new_student)

    def update_student(self, student_id: int, student: StudentUpdate) -> StudentResponse:
        existing_student = self.show_student(student_id)
        existing_student.name = student.name
        return StudentResponse.from_orm(existing_student)

    def delete_student(self, student_id: int) -> None:
        student = self.show_student(student_id)
        self.students.remove(student)
        
    def multiply(self, student_id: int)  -> None:
        student = self.show_student(student_id * 2)
        return student
        
        
class SchoolService:
    def __init__(self):
        self.schools = schools_db

    def list_schools(self) -> List[SchoolResponse]:
        return [SchoolResponse.from_orm(school) for school in self.schools]

    def show_school(self, school_id: int) -> SchoolResponse:
        school = next((school for school in self.schools if school.id == school_id), None)
        if school is None:
            raise CustomHTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="School not found"
            )
        return SchoolResponse.from_orm(school)

    def create_school(self, school: SchoolCreate) -> SchoolResponse:
        new_id = max((s.id for s in self.schools), default=0) + 1
        new_school = School(id=new_id, name=school.name)
        self.schools.append(new_school)
        return SchoolResponse.from_orm(new_school)

    def update_school(self, school_id: int, school: SchoolUpdate) -> SchoolResponse:
        existing_school = self.show_school(school_id)
        existing_school.name = school.name
        return SchoolResponse.from_orm(existing_school)

    def delete_school(self, school_id: int) -> None:
        school = self.show_school(school_id)
        self.schools.remove(school)
        
        
        