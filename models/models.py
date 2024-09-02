from typing import List
import mysql.connector
from mysql.connector import Error
import logging
from fastapi import HTTPException
from schemas.schemas import SchoolRequest, StudentRequest, StudentResponse, StudentWithSchoolResponse,StudentBase,SchoolBase
from util.helper import Students,Schools

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='fastapi_db',
            user='root',
            password=''
        )
        logger.info("Koneksi database berhasil dibuat")
        return connection
    except Error as e:
        logger.error(f"Error connecting to MySQL database: {e}")
        return None

class Student:
    def __init__(self, id: int, name: str, school_id: int, school_name: str):
        self.id = id
        self.name = name
        self.school_id = school_id
        self.school_name = school_name

def get_all_students():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
            SELECT s.id as student_id, s.name as student_name, s.school_id,
            sch.name as school_name
            FROM students s
            INNER JOIN schools sch ON s.school_id = sch.id
            """)
            students = cursor.fetchall()

            if not students:
                raise HTTPException(status_code=404, detail="Tidak ada siswa yang ditemukan")

            responses = Students.convert_to_json_students(students)
            return responses
        except Error as e:
            logger.error(f"Error saat mengambil data siswa dan sekolah: {e}")
            raise HTTPException(status_code=500, detail="Terjadi kesalahan internal server")
        finally:
            cursor.close()
            connection.close()
    else:
        raise HTTPException(status_code=500, detail="Tidak dapat membuat koneksi database")

def get_student_by_id_from_db(student_id: int):
    connection = get_db_connection()  
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
            SELECT s.id as student_id, s.name as student_name, s.school_id,
            sch.name as school_name
            FROM students s
            INNER JOIN schools sch ON s.school_id = sch.id
            WHERE s.id = %s
            """
            cursor.execute(query, (student_id))
            student = cursor.fetchone()
            if student is None:
                raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")
            responses = Students.convert_to_json_students(student)
            return responses         
        except Error as e:
            logger.error(f"Error database saat mengambil data siswa: {str(e)}")
        finally:     
            cursor.close()
            connection.close()
            
def get_student_by_name_from_db(student_name:str):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
            SELECT s.id as student_id, s.name as student_name, s.school_id,
            sch.name as school_name
            FROM students s
            INNER JOIN schools sch ON s.school_id = sch.id
            WHERE LOWER(s.name) LIKE LOWER(%s)
            """
            cursor.execute(query, (f"%{student_name}%",))
            students = cursor.fetchall()
            if not students:
                raise HTTPException(status_code=404, detail="Tidak ada siswa yang ditemukan")
            responses = Students.convert_to_json_students_name(students)
            return responses
        except Error as e:
            logger.error(f"Error database saat mengambil data siswa: {str(e)}")
        finally:
            cursor.close()
            connection.close()

def add_student(student:StudentRequest):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "INSERT INTO students (name, school_id) VALUES (%s,%s)"
            values = (student.name,student.school_id)
            cursor.execute(query, values)
            connection.commit()
            return cursor.lastrowid
        except Error as e:
            logger.error(f"Error menambahkan siswa ke database: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    return None

def update_student(student:StudentRequest,student_id:int):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "UPDATE students SET name = %s, school_id = %s WHERE id = %s"
            values = (student.name,student.school_id,student_id)
            cursor.execute(query,values)
            connection.commit()
            return cursor.rowcount
        except Error as e:
            logger.error(f"Error database saat mengambil data siswa: {str(e)}")
        finally:
            cursor.close()
            connection.close()

def delete_student(student_id: int):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "DELETE FROM `students` WHERE id = %s"
            values = (student_id, )
            cursor.execute(query,values)
            connection.commit()
            return cursor.rowcount
        except Error as e:
            logger.error(f"Error database saat mengambil data siswa: {str(e)}")
            return None
        finally:
            cursor.close()
            connection.close()
            
students_db = get_all_students()


class School:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

def get_all_schools():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM schools")
            schools = cursor.fetchall()
            responses = Schools.convert_to_json_schools(schools)
            return responses
        finally:
            cursor.close()
            connection.close()
    return []

def get_school_by_id_from_db(school_id: int):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            school_query = "SELECT id, name FROM schools WHERE id = %s"
            cursor.execute(school_query, (school_id,))
            school = cursor.fetchone()
            
            responses = Schools.convert_to_json_schools(school)
            
            return responses
        except Error as e:
            logger.error(f"Error saat mengambil data sekolah dan siswa: {e}")
            raise HTTPException(status_code=500, detail="Terjadi kesalahan internal server")
        finally:
            cursor.close()
            connection.close()


def add_school(school:SchoolBase):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "INSERT INTO schools (id,name) VALUES (%s,%s)"
            values = (school.id,school.name)
            cursor.execute(query, values)
            connection.commit()
            return cursor.lastrowid
        except Error as e:
            logger.error(f"Error menambahkan sekolah ke database: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    return None

def update_school(school_id:int,school:SchoolRequest):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "UPDATE schools SET name = %s WHERE id = %s"
            values = (school.name,school_id)
            cursor.execute(query,values)
            connection.commit()
            return cursor.rowcount
        except Error as e:
            logger.error(f"error saat mengupdate sekolah: {e}")
        finally:
            cursor.close()
            connection.close()
            
def delete_school(school_id:int):
    connection = get_db_connection()
    if connection:
        try :
            cursor = connection.cursor()
            query = "DELETE FROM `schools` WHERE id = %s"
            values = (school_id, )
            cursor.execute(query,values)
            connection.commit()
            return cursor.rowcount
        except Error as e:
            logger.error(f"Error database saat mengambil data sekolah: {str(e)}")
            return None
        finally:
            cursor.close()
            connection.close()
            
    
schools_db = get_all_schools()