# Task 1: Student Result Management API

### Goal
Build a FastAPI-based API to manage student scores, compute grades, and persist data.

### Features
- **Student Model:** Pydantic model for a student with `name`, `subject_scores`, `average`, and `grade`.
- **Endpoints:**
  - `POST /students/`: Add a new student record.
  - `GET /students/{name}`: Retrieve a specific student by name.
  - `GET /students/`: Retrieve a list of all students.
- **Data Persistence:** Student records are loaded from and saved to `students.json` on each change.
- **Error Handling:** Robust error handling is implemented using `HTTPException` for invalid input and non-existent students.
- **Console Logging:** Uses `colorama` for clear, color-coded messages in the terminal.

### How to Run
1. Navigate to the `task_1_student_api/` directory.
2. Install dependencies: `pip install fastapi "uvicorn[standard]" colorama`
3. Run the application: `uvicorn main:app --reload`
4. Access the interactive documentation at `http://127.0.0.1:8000/docs` to test the endpoints.