# Task 3: Job Application Tracker API

### Goal
Build a FastAPI-based API to track job applications, including status and application date.

### Features
- **Data Model:** Uses Pydantic models to define the structure of a `JobApplication`.
- **Status Validation:** The application `status` is restricted to a predefined set of values ("Pending", "Interviewing", "Rejected", "Accepted") using Python's `enum.Enum`, preventing invalid inputs.
- **Automatic Fields:** The `id` is automatically generated, and the `date_applied` defaults to the current timestamp.
- **Data Persistence:** Application records are loaded from and saved to `applications.json` on startup and shutdown.
- **Modular Design:** Data handling logic is separated into a dedicated `file_handler.py` module.
- **Error Handling:** Appropriate `HTTPException` is raised for requests to non-existent applications.
- **Console Logging:** Uses `colorama` for clear, color-coded messages.

### Pydantic Models
- `JobApplicationBase`: The input model for creating a new application (contains `company`, `title`, `status`).
- `JobApplication`: The full model for a returned application (includes `id` and `date_applied`).
- `ApplicationStatus`: An `enum.Enum` to validate the `status` field.

### API Endpoints

- **`POST /applications/`**
  - **Description:** Creates a new job application.
  - **Example Request Body:**
    ```json
    {
      "company": "Example Corp.",
      "title": "Senior Engineer",
      "status": "Interviewing"
    }
    ```

- **`GET /applications/{app_id}`**
  - **Description:** Retrieves a specific application by its unique ID.

- **`GET /applications/`**
  - **Description:** Retrieves a list of all tracked job applications.

### How to Run
1. Navigate to the `task_3_job_application_tracker/` directory.
2. Ensure your virtual environment is activated and dependencies (`fastapi`, `uvicorn`, `colorama`) are installed.
3. Run the application: `uvicorn main:app --reload`
4. Access the interactive documentation at `http://127.0.0.1:8000/docs` to test the endpoints.