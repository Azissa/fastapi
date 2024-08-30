from schemas.schemas import StudentWithSchoolResponse,SchoolResponse

class Students:
  def convert_to_json_students(students):
      if isinstance(students, dict):
          return StudentWithSchoolResponse(
              id=students['student_id'],
              name=students['student_name'],
              school_id=students['school_id'],
              school_name=students['school_name']
          )

      
      responses = [
          StudentWithSchoolResponse(
              id=student[0],
              name=student[1],
              school_id=student[2],
              school_name=student[3]
          ) for student in students
      ]
      return responses

class Schools: 
  def convert_to_json_schools(schools):
      if isinstance(schools, dict):
          return SchoolResponse(
          id=schools['id'],
          name=schools['name']
        )
      
      responses = [SchoolResponse(
                id=school[0],
                name=school[1]
            )for school in schools ]   
      return responses
    
    
    
  