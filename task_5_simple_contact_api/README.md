# Task 5: Simple Contact API

### Goal
Build a simple API to manage contact information, with data stored in memory.

### Features
- **In-Memory Storage:** Unlike previous tasks, this API uses a simple Python dictionary to store data. All data is lost when the server is shut down.
- **Data Model:** Uses Pydantic models (`ContactBase` for input, `Contact` for output) to validate contact data, including a validated email format.
- **Search Functionality:** Implements a search endpoint that uses a query parameter to filter contacts by name.
- **RESTful Endpoints:** Provides full CRUD (Create, Read, Update, Delete) functionality.
- **Error Handling:** Appropriate `HTTPException` is raised for requests to non-existent contacts.
- **Console Logging:** Uses `colorama` for clear, color-coded messages.

### Pydantic Models
- `ContactBase`: The input model for creating or updating a contact (contains `name`, `email`).
- `Contact`: The full model for a returned contact (includes `id`, `name`, `email`).

### API Endpoints
- **`POST /contacts/`**
  - **Description:** Creates a new contact and adds it to the in-memory database.
- **`GET /contacts/{contact_id}`**
  - **Description:** Retrieves a specific contact by its unique ID.
- **`GET /contacts/search/`**
  - **Description:** Searches for contacts whose names contain a given query string.
  - **Query Parameter:** `name` (required string)
- **`PUT /contacts/{contact_id}`**
  - **Description:** Updates the name and email of an existing contact.
- **`DELETE /contacts/{contact_id}`**
  - **Description:** Deletes a contact by its ID.

### How to Run
1. Navigate to the `task_5_simple_contact_api/` directory.
2. Ensure your virtual environment is activated and dependencies (`fastapi`, `uvicorn`, `colorama`) are installed.
3. Run the application: `uvicorn main:app --reload`
4. Access the interactive documentation at `http://127.0.0.1:8000/docs` to test the endpoints.