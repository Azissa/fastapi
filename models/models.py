from typing import List

class Student:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

class School:
    def __init__(self, id: int, name: str):
        self.id = id  
        self.name = name


students_db: List[Student] = []
schools_db: List[School] = []
