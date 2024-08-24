from fastapi import APIRouter, HTTPException, Body
from typing import List
from schemas.schemas import SchoolCreate, SchoolUpdate, SchoolResponse, StudentCreate, StudentUpdate, StudentResponse,SchoolWithStudent
from services.service import SchoolService, StudentService
from models.models import get_db_connection,add_school,add_student
import logging
from mysql.connector import Error

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

            student_query = "SELECT id, name, school_id FROM students WHERE name = %s AND school_id = %s"
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

@router.post("/students/", response_model=StudentResponse)
async def create_student(student: StudentCreate):
    new_student_id = add_student(student.name, student.school_id)
    if new_student_id:
        return StudentResponse(id=new_student_id, name=student.name, school_id=student.school_id)
    else:
        raise HTTPException(status_code=500, detail="Gagal menambahkan siswa")


@router.put("/students/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student: StudentUpdate):
    return student_service.update_student(student_id, student)

@router.delete("/students/{student_id}")
def delete_student(student_id: int):
    student_service.delete_student(student_id)
    return {"detail": "Student deleted"}

@router.get("/multiply/{multiply}")
def getMultiply(multiply:int):
    return student_service.getMultiply(multiply)
