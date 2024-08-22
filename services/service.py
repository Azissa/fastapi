from typing import List
from models.models import School, Student, get_all_students, get_all_schools, get_db_connection
from schemas.schemas import SchoolCreate, SchoolUpdate, SchoolResponse, StudentCreate, StudentUpdate, StudentResponse
from exceptions.custom_exceptions import CustomHTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
import logging
from mysql.connector import Error

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StudentService:
    def __init__(self):
        self.students = get_all_students()

    def list_students(self) -> List[Student]:
        return get_all_students()

    def show_student(self, student_id: int) -> StudentResponse:
        logger.info(f"Mencoba mendapatkan siswa dengan ID: {student_id}")
        try:
            student = self.get_student_by_id(student_id)
            if student is None:
                logger.warning(f"Siswa dengan ID {student_id} tidak ditemukan di database")
                return None
            logger.info(f"Siswa ditemukan: {student}")
            return StudentResponse.from_orm(student)
        except Exception as e:
            logger.error(f"Error saat mendapatkan siswa: {str(e)}")
            raise

    def get_student_by_id(self, student_id: int) -> Student:
        logger.info(f"Mencoba mendapatkan siswa dengan ID: {student_id}")
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
                result = cursor.fetchone()
                if result:
                    logger.info(f"Data siswa ditemukan: {result}")
                    logger.info(f"Kunci dalam result: {result.keys()}")
                    # Ubah 'ID' menjadi 'id'
                    result['id'] = result.pop('id')
                    return Student(**result)
                logger.warning(f"Tidak ada data siswa dengan ID {student_id}")
            except Error as e:
                logger.error(f"Error database saat mengambil data siswa: {str(e)}")
            finally:
                cursor.close()
                connection.close()
        else:
            logger.error("Tidak dapat membuat koneksi database")
        return None

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
        
    def getMultiply(self,multiply: int)  -> None:    
        return multiply * multiply
    
        
        
class SchoolService:
    def __init__(self):
        self.schools = get_all_schools()

    def list_schools(self) -> List[SchoolResponse]:
        return [SchoolResponse.from_orm(school) for school in get_all_schools()]

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