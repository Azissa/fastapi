import secrets
from datetime import datetime,timedelta,timezone
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException, Body,Security,status
from typing import List,Annotated
from fastapi.security import HTTPBasic,HTTPBasicCredentials,OAuth2PasswordBearer,OAuth2PasswordRequestForm,SecurityScopes
from grpc import Status
from pydantic import ValidationError
from schemas.schemas import SchoolCreate, SchoolUpdate, SchoolResponse, StudentCreate, StudentRequest, StudentUpdate, StudentResponse,SchoolWithStudent,StudentWithSchoolResponse, Token, TokenData, User, UserInDB
from services.service import SchoolService, StudentService
from models.models import get_db_connection,add_school,add_student
import logging
from mysql.connector import Error


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()  
security = HTTPBasic()
school_service = SchoolService()
student_service = StudentService()


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Chains",
        "email": "alicechains@example.com",
        "hashed_password": "$2b$12$gSvqqUPvlXP2tfVFaWK1Be7DlH.PKZbv5H8KnzzVgXXbVxpva.pFm",
        "disabled": True,
    },
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={"me": "Read information about the current user.", "items": "Read items."},
)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (InvalidTokenError, ValidationError):
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Security(get_current_user, scopes=["me"])],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": form_data.scopes},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
):
    return [{"item_id": "Foo", "owner": current_user.username}]


@router.get("/status/")
async def read_system_status(current_user: Annotated[User, Depends(get_current_user)]):
    return {"status": "ok"}






class CurrentUser:
    @staticmethod
    def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
        current_username_bytes = credentials.username.encode("utf8")
        correct_username_bytes = b"ajis"
        is_correct_username = secrets.compare_digest(
            current_username_bytes, correct_username_bytes
        )
        current_password_bytes = credentials.password.encode("utf8")
        correct_password_bytes = b"squit456"
        is_correct_password = secrets.compare_digest(
            current_password_bytes, correct_password_bytes
        )
        if not (is_correct_username and is_correct_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Basic"},
            )

        logger.info("berhasil masuk")
        return credentials.username

@router.get("/users/me", response_model=str)  
def read_current_user(current_username: str = Depends(CurrentUser.get_current_username)):
    return current_username

@router.get("/multiply/{multiply}")
def getMultiply(multiply:int):
    return student_service.getMultiply(multiply)

# School Endpoints
@router.get("/schools", response_model=List[SchoolResponse])
def list_schools():
    return school_service.list_schools()

@router.get("/school/show/byid/{school_id}", response_model=SchoolResponse)
def find_school_by_id(school_id:int):
    return school_service.get_school_by_id(school_id)

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

@router.put("/schools/update/{school_id}", response_model=SchoolResponse)
def update_school(school_id: int, school: SchoolUpdate):
    return school_service.put_school(school_id, school)

@router.delete("/schools/delete/{school_id}")
def del_school(school_id: int):
    school_service.del_school(school_id)
    return {"detail": "School deleted"}

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

@router.put("/student/update/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student: StudentUpdate):
    return student_service.put_student(student_id, student)

@router.put("/student/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student: StudentUpdate):
    return student_service.update_student(student_id, student)

@router.delete("/student/delete/{student_id}")
def del_student(student_id:int):
    student_service.del_student(student_id)
    return {"detail": "Student deleted"}

@router.delete("/student/{student_id}")
def delete_student(student_id: int):
    student_service.delete_student(student_id)
    return {"detail": "Student deleted"}


