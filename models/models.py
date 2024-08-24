from typing import List
import mysql.connector
from mysql.connector import Error
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Student:
    def __init__(self, id: int, name: str, school_id: int):
        self.id = id
        self.name = name
        self.school_id = school_id

class School:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

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

def get_all_students():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT id, name, school_id FROM students")
            students = [Student(id=row[0], name=row[1], school_id=row[2]) for row in cursor.fetchall()]
            return students
        finally:
            cursor.close()
            connection.close()
    return []

def get_all_schools():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM schools")
            schools = [School(id=row[0], name=row[1]) for row in cursor.fetchall()]
            return schools
        finally:
            cursor.close()
            connection.close()
    return []


def add_student(name: str, school_id: int):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "INSERT INTO students (name, school_id) VALUES (%s, %s)"
            values = (name, school_id)
            cursor.execute(query, values)
            connection.commit()
            logger.info(f"Siswa baru '{name}' berhasil ditambahkan ke database")
            return cursor.lastrowid
        except Error as e:
            logger.error(f"Error menambahkan siswa ke database: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    return None

def add_school(name: str):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "INSERT INTO schools (name) VALUES (%s)"
            values = (name,)
            cursor.execute(query, values)
            connection.commit()
            logger.info(f"Sekolah baru '{name}' berhasil ditambahkan ke database")
            return cursor.lastrowid
        except Error as e:
            logger.error(f"Error menambahkan sekolah ke database: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    return None


schools_db = get_all_schools()
students_db = get_all_students()