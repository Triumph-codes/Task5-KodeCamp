# Task 4: Notes App API

### Goal
Create a simple API to manage notes, with each note stored as a separate file on the server's file system.

### Features
- **Data Model:** Uses Pydantic models (`NoteBase` for input, `Note` for output) to validate note data.
- **File System Storage:** Each note is stored as a separate `.json` file in a dedicated `notes/` directory.
- **Modular Design:** All file system interaction logic is encapsulated in a `file_storage.py` module.
- **Unique IDs:** Uses Python's `uuid` library to generate unique identifiers for each note, ensuring no two notes have the same ID.
- **RESTful Endpoints:** Implements full CRUD (Create, Read, Update, Delete) functionality with clear and intuitive HTTP verbs.
- **Error Handling:** Appropriate `HTTPException` is raised for file-not-found scenarios.
- **Console Logging:** Uses `colorama` for clear, color-coded messages.

### Pydantic Models
- `NoteBase`: The input model for creating or updating a note (contains `title`, `content`).
- `Note`: The full model for a returned note (includes `id`, `title`, `content`).

### API Endpoints

- **`POST /notes/`**
  - **Description:** Creates a new note and saves it as a file.
- **`GET /notes/{note_id}`**
  - **Description:** Retrieves a specific note by its unique ID.
- **`PUT /notes/{note_id}`**
  - **Description:** Updates the content of an existing note.
- **`DELETE /notes/{note_id}`**
  - **Description:** Deletes a note by its ID.
- **`GET /notes/`**
  - **Description:** Retrieves a list of all notes.

### How to Run
1. Navigate to the `task_4_notes_app/` directory.
2. Ensure your virtual environment is activated and dependencies (`fastapi`, `uvicorn`, `colorama`) are installed.
3. Run the application: `uvicorn main:app --reload`
4. Access the interactive documentation at `http://127.0.0.1:8000/docs` to test the endpoints.