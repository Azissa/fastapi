from typing import List
import mysql.connector
from mysql.connector import Error
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Student:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

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
            cursor.execute("SELECT * FROM students")
            students = [Student(id=row[0], name=row[1]) for row in cursor.fetchall()]
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

def create_tables():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL
                )
            """)
            connection.commit()
            print("Tabel 'students' berhasil dibuat atau sudah ada.")
        except Error as e:
            print(f"Error membuat tabel: {e}")
        finally:
            cursor.close()
            connection.close()

# Inisialisasi database sekolah dan siswa
create_tables()
schools_db = get_all_schools()
students_db = get_all_students()
