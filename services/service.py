from typing import List

from fastapi import HTTPException
from models.models import School, Student, delete_school, delete_student, get_all_students, get_all_schools, get_db_connection, get_school_by_id_from_db,get_student_by_id_from_db,add_student,add_school, get_student_by_name_from_db, update_school,update_student
from schemas.schemas import SchoolCreate, SchoolRequest, SchoolUpdate, SchoolResponse, StudentCreate, StudentRequest, StudentUpdate, StudentResponse,StudentWithSchoolResponse,StudentBase
from exceptions.custom_exceptions import CustomHTTPException
from starlette.status import HTTP_404_NOT_FOUND
import logging
from mysql.connector import Error


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def getMultiply(multiply: int)  -> None:    
    return multiply * multiply

class StudentService:
    def __init__(self):
        self.students = get_all_students()

    def list_students(self) -> List[Student]:
        return get_all_students()

    def get_student_by_id(self,student_id: int) -> StudentWithSchoolResponse:
        try:
            student = get_student_by_id_from_db(student_id)
            if student is None:
                raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")
            return student
        except Exception as e:
            logger.error(f"Error saat mendapatkan siswa: {str(e)}")
        
    def get_student_by_name(self,student_name:str) -> StudentWithSchoolResponse:
        try:
            students = get_student_by_name_from_db(student_name)
            if students is None:
                raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")
            return students
        except Exception as e:
            logger.error(f"Error saat mendapatkan siswa: {str(e)}")
        
    def post_student(self, student: StudentRequest) -> StudentResponse:
        new_student_id = add_student(student)
        if new_student_id:
            return StudentResponse(id=new_student_id ,name=student.name, school_id=student.school_id)
        else:
            raise HTTPException(status_code=500, detail="Gagal menambahkan siswa")

    def put_student(self, student_id: int, student: StudentUpdate) -> StudentResponse:
        try:
            updated_rows = update_student(student, student_id)
            if updated_rows and updated_rows > 0:
                return StudentResponse(id=student_id, name=student.name, school_id=student.school_id)
            else:
                raise HTTPException(status_code=404, detail="Siswa tidak ditemukan atau tidak ada perubahan data")
        except Exception as e:
            logger.error(f"Error saat mendapatkan siswa: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    def del_student(self, student_id: int) -> dict:
        deleted_rows = delete_student(student_id) 
        if deleted_rows and deleted_rows > 0:
            return {"message": "Siswa berhasil dihapus", "deleted_id": student_id}
        else:
            raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")



class SchoolService:
    def __init__(self):
        self.schools = get_all_schools()

    def list_schools(self) -> List[SchoolResponse]:
        return [SchoolResponse.from_orm(school) for school in get_all_schools()]
    
    def get_school_by_id(self,school_id: int) -> SchoolResponse:
        try:
            school = get_school_by_id_from_db(school_id)
            if school is None:
                raise HTTPException(status_code=404, detail="Sekolah tidak ditemukan")
            return school
        except Exception as e:
            logger.error(f"Error saat mendapatkan sekolah: {str(e)}")

    def post_school(self, school: SchoolRequest) -> SchoolResponse:
        new_school_id = add_school(school)
        if new_school_id:
            return SchoolResponse(id=new_school_id,name=school.name)
        else:
            raise HTTPException(status_code=500, detail="Gagal menambahkan sekolah")

    def put_school(self, school_id:int, school:SchoolUpdate) -> SchoolResponse:
        try:
            updated_rows = update_school(school_id, school)
            if updated_rows and updated_rows > 0:
                return SchoolResponse(id=school_id, name=school.name)
            else:
                raise HTTPException(status_code=404, detail="Sekolah tidak ditemukan atau tidak ada perubahan data")
        except Exception as e:
            logger.error(f"Error saat mendapatkan sekolah: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    def del_school(self, school_id: int) -> dict:
        deleted_rows = delete_school(school_id) 
        if deleted_rows and deleted_rows > 0:
            return {"message": "Siswa berhasil dihapus", "deleted_id": school_id}
        else:
            raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")

    def delete_school(self, school_id: int) -> None:
        school = self.show_school(school_id)
        self.schools.remove(school)
        school = self.show_school(school_id)
        self.schools.remove(school)