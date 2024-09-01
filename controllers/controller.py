from fastapi import APIRouter, HTTPException, Body
from typing import List
from schemas.schemas import SchoolCreate, SchoolUpdate, SchoolResponse, StudentCreate, StudentRequest, StudentUpdate, StudentResponse,SchoolWithStudent,StudentWithSchoolResponse
from services.service import SchoolService, StudentService
from models.models import get_db_connection,add_school,add_student
import logging
from mysql.connector import Error
from util.helper import Students

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()  
school_service = SchoolService()
student_service = StudentService()

@router.get("/multiply/{multiply}")
def getMultiply(multiply:int):
    return student_service.getMultiply(multiply)

# School Endpoints
@router.get("/schools", response_model=List[SchoolResponse])
def list_schools():
    return school_service.list_schools()

@router.get("/schoolbyid/{school_id}", response_model=SchoolResponse)
def find_school_by_id(school_id:int):
    return school_service.find_school_by_id(school_id)

@router.get("/schools/{school_id}/students", response_model=SchoolWithStudent)
def read_school_with_all_students(school_id: int):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)

            school_query = "SELECT id, name FROM schools WHERE id = %s"
            cursor.execute(school_query, (school_id,))
            school = cursor.fetchone()

            if school is None:
                raise HTTPException(status_code=404, detail="Sekolah tidak ditemukan")

            students_query = "SELECT id, name, school_id FROM students WHERE school_id = %s"
            cursor.execute(students_query, (school_id,))
            students = cursor.fetchall()

            student_responses = [StudentResponse(id=student['id'], name=student['name'], school_id=student['school_id']) for student in students]

            result = SchoolWithStudent(
                id=school['id'],
                name=school['name'],
                students=student_responses
            )

            return result
        except Error as e:
            logger.error(f"Error saat mengambil data sekolah dan siswa: {e}")
            raise HTTPException(status_code=500, detail="Terjadi kesalahan internal server")
        finally:
            cursor.close()
            connection.close()
    else:
        raise HTTPException(status_code=500, detail="Tidak dapat membuat koneksi database")
    
@router.get("/schools/{school_id}/students/{student_id}", response_model=SchoolWithStudent)
def read_school_with_student(school_id: int, student_id: int):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)

            school_query = "SELECT id, name FROM schools WHERE id = %s"
            cursor.execute(school_query, (school_id,))
            school = cursor.fetchone()

            if school is None:
                raise HTTPException(status_code=404, detail="Sekolah tidak ditemukan")

            student_query = "SELECT id, name, school_id FROM students WHERE id = %s AND school_id = %s"
            cursor.execute(student_query, (student_id, school_id))
            student = cursor.fetchone()

            if student is None:
                raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")

            student_response = StudentResponse(id=student['id'], name=student['name'], school_id=student['school_id'])

            result = SchoolWithStudent(
                id=school['id'],
                name=school['name'],
                students=[student_response]
            )

            return result
        except Error as e:
            logger.error(f"Error saat mengambil data sekolah dan siswa: {e}")
            raise HTTPException(status_code=500, detail="Terjadi kesalahan internal server")
        finally:
            cursor.close()
            connection.close()
    else:
        raise HTTPException(status_code=500, detail="Tidak dapat membuat koneksi database")
    
@router.get("/schools/{school_id}/students/name/{student_name}", response_model=SchoolWithStudent)
def read_school_with_student(school_id: int, student_name: str):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)

            school_query = "SELECT id, name FROM schools WHERE id = %s"
            cursor.execute(school_query, (school_id,))
            school = cursor.fetchone()

            if school is None:
                raise HTTPException(status_code=404, detail="Sekolah tidak ditemukan")

            student_query = "SELECT id, name, school_id FROM students WHERE LOWER(name) LIKE LOWER(%s) AND school_id = %s"
            cursor.execute(student_query, (student_name, school_id))
            student = cursor.fetchone()

            if student is None:
                raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")

            student_response = StudentResponse(id=student['id'], name=student['name'], school_id=student['school_id'])

            result = SchoolWithStudent(
                id=school['id'],
                name=school['name'],
                students=[student_response]
            )

            return result
        except Error as e:
            logger.error(f"Error saat mengambil data sekolah dan siswa: {e}")
            raise HTTPException(status_code=500, detail="Terjadi kesalahan internal server")
        finally:
            cursor.close()
            connection.close()
    else:
        raise HTTPException(status_code=500, detail="Tidak dapat membuat koneksi database")

@router.post("/addschool", response_model=SchoolResponse)
def post_school(school:SchoolCreate):
    return school_service.post_school(school)

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
@router.get("/student/showall", response_model=List[StudentWithSchoolResponse])
def list_students():
    return student_service.list_students()

@router.get("/student/show/byid/{student_id}", response_model=StudentWithSchoolResponse)
def get_student_by_id(student_id: int):
    student = student_service.get_student_by_id(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")
    return student

@router.get("/student/show/byname/{student_name}", response_model=List[StudentWithSchoolResponse])
def get_student_by_name(student_name: str):
    students = student_service.get_student_by_name(student_name)
    print(students)
    if students is None:
        raise HTTPException(status_code=404, detail="siswa tidak ditemukan")
    return students

@router.post("/student/add", response_model=StudentResponse)
def post_student(student_request:StudentRequest):
    return student_service.post_student(student_request)

@router.put("/students/update/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student: StudentUpdate):
    return student_service.update_student(student_id, student)

@router.delete("/students/{student_id}")
def delete_student(student_id: int):
    student_service.delete_student(student_id)
    return {"detail": "Student deleted"}


