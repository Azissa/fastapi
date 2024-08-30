import httpx


student_data = {
    "name": "John Doe",
    "school_id": 1 
}

url = "http://localhost:8000/addstudent"  

response = httpx.post(url, json=student_data)

if response.status_code == 200:
    print("Siswa berhasil ditambahkan:", response.json())
else:
    print("Gagal menambahkan siswa:", response.status_code, response.text)