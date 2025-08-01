from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, RootModel, model_validator  
from typing import Dict, List, Optional, Any 
from contextlib import asynccontextmanager
import json
import os
from colorama import Fore, Style, init 

init(autoreset=True)

# --- Constants ---
STUDENTS_FILE = "students.json"

# --- Pydantic Models ---
class SubjectScores(RootModel):
    root: Dict[str, float] 

    @model_validator(mode='after')
    def validate_scores(self):
        for subject, score in self.root.items():
            if not (0 <= score <= 100):
                raise ValueError(f"Score for {subject} must be between 0 and 100.")
        return self

class StudentBase(BaseModel):
    name: str = Field(..., min_length=1)
    subject_scores: Dict[str, float] = Field(...)

    @model_validator(mode='after')
    def validate_scores(self):
        for subject, score in self.subject_scores.items():
            if not (0 <= score <= 100):
                raise ValueError(f"Score for {subject} must be between 0 and 100.")
        return self

class Student(StudentBase):
    average: float = Field(...)
    grade: str = Field(...)

# --- Database and Utility Functions ---
students_db: Dict[str, Student] = {}

def load_students_data() -> None:
    global students_db
    if os.path.exists(STUDENTS_FILE):
        try:
            with open(STUDENTS_FILE, "r") as f:
                data = json.load(f)
                students_db = {
                    name: Student(**student_data)
                    for name, student_data in data.items()
                }
            print(f"{Fore.GREEN}INFO: Loaded {len(students_db)} students{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}ERROR loading data: {e}{Style.RESET_ALL}")
            students_db = {}

def save_students_data() -> None:
    try:
        with open(STUDENTS_FILE, "w") as f:
            json.dump(
                {name: student.model_dump() for name, student in students_db.items()},
                f, indent=4
            )
    except Exception as e:
        print(f"{Fore.RED}ERROR saving data: {e}{Style.RESET_ALL}")

def calculate_average_and_grade(scores: Dict[str, float]) -> tuple[float, str]:
    if not scores: return 0.0, "N/A"
    average = sum(scores.values()) / len(scores)
    if average >= 90: return round(average, 2), "A"
    elif average >= 80: return round(average, 2), "B"
    elif average >= 70: return round(average, 2), "C"
    elif average >= 60: return round(average, 2), "D"
    return round(average, 2), "F"

# --- FastAPI App ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"{Fore.MAGENTA}Starting up...{Style.RESET_ALL}")
    load_students_data()
    yield
    print(f"{Fore.MAGENTA}Shutting down...{Style.RESET_ALL}")

app = FastAPI(
    title="Student API",
    description="Manages student scores and grades",
    version="1.0.0",
    lifespan=lifespan
)

# --- API Endpoints ---
@app.post("/students/", response_model=Student, status_code=201)
async def create_student(student_data: StudentBase):
    name_lower = student_data.name.lower()
    if name_lower in students_db:
        raise HTTPException(409, detail="Student already exists")
    
    avg, grade = calculate_average_and_grade(student_data.subject_scores)
    student = Student(
        name=student_data.name,
        subject_scores=student_data.subject_scores,
        average=avg,
        grade=grade
    )
    students_db[name_lower] = student
    save_students_data()
    return student

@app.get("/students/{name}", response_model=Student)
async def get_student(name: str):
    if (student := students_db.get(name.lower())) is None:
        raise HTTPException(404, detail="Student not found")
    return student

@app.get("/students/", response_model=List[Student])
async def get_all_students():
    return list(students_db.values())

@app.put("/students/{name}", response_model=Student)
async def update_student(name: str, student_data: StudentBase):
    name_lower = name.lower()
    if name_lower not in students_db:
        raise HTTPException(404, detail="Student not found")
    if student_data.name.lower() != name_lower:
        raise HTTPException(400, detail="Name mismatch")
    
    avg, grade = calculate_average_and_grade(student_data.subject_scores)
    student = Student(
        name=student_data.name,
        subject_scores=student_data.subject_scores,
        average=avg,
        grade=grade
    )
    students_db[name_lower] = student
    save_students_data()
    return student

@app.delete("/students/{name}", status_code=204)
async def delete_student(name: str):
    if (name_lower := name.lower()) not in students_db:
        raise HTTPException(404, detail="Student not found")
    del students_db[name_lower]
    save_students_data()
    return None 