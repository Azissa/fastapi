from fastapi import APIRouter, HTTPException
from typing import List
from schemas.schemas import SchoolCreate, SchoolUpdate, SchoolResponse, StudentCreate, StudentUpdate, StudentResponse
from services.service import SchoolService, StudentService
from models.models import get_db_connection
import logging
from mysql.connector import Error

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()  # Pastikan baris ini ada di awal file
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
async def get_student(student_id: int):
    logger.info(f"Mencoba mengambil siswa dengan ID: {student_id}")
    student = student_service.show_student(student_id)
    if student is None:
        logger.warning(f"Siswa dengan ID {student_id} tidak ditemukan")
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")
    logger.info(f"Siswa ditemukan: {student}")
    return student

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

@router.get("/multiply/{multiply}")
def getMultiply(multiply:int):
    return student_service.getMultiply(multiply)
@router.get("/debug/students")
async def debug_students():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM students")
            results = cursor.fetchall()
            return {"students": results}
        except Error as e:
            return {"error": str(e)}
        finally:
            cursor.close()
            connection.close()
    return {"error": "Tidak dapat membuat koneksi database"}