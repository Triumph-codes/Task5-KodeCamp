# task_4_notes_app/main.py

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List
from contextlib import asynccontextmanager
from colorama import Fore, Style, init

from file_storage import setup_directory, create_note, get_note, update_note, delete_note, get_all_notes

# Initialize colorama
init(autoreset=True)

# --- Pydantic Models ---
class NoteBase(BaseModel):
    """Base model for creating or updating a note."""
    title: str = Field(..., min_length=1, description="Title of the note")
    content: str = Field(..., description="Content of the note")

class Note(NoteBase):
    """Full model for a note, including its unique ID."""
    id: str = Field(..., description="Unique identifier for the note")

# --- FastAPI App Initialization ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"{Fore.MAGENTA}--- API Startup: Initializing file storage ---{Style.RESET_ALL}")
    setup_directory()
    yield
    # Shutdown
    print(f"{Fore.MAGENTA}--- API Shutdown ---{Style.RESET_ALL}")

app = FastAPI(
    title="Notes App API",
    description="API for managing notes stored as individual files.",
    version="1.0.0",
    lifespan=lifespan
)

# --- API Endpoints ---

@app.post(
    "/notes/",
    response_model=Note,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new note",
    description="Creates a new note with a unique ID and saves it to a file."
)
async def create_new_note(note: NoteBase):
    try:
        created_note = create_note(note.title, note.content)
        return created_note
    except IOError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the note: {e}"
        )

@app.get(
    "/notes/{note_id}",
    response_model=Note,
    summary="Retrieve a specific note",
    description="Returns a note by its unique ID."
)
async def get_specific_note(note_id: str):
    note_data = get_note(note_id)
    if not note_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID '{note_id}' not found."
        )
    print(f"{Fore.BLUE}INFO: Retrieved note with ID '{note_id}'.{Style.RESET_ALL}")
    return note_data

@app.put(
    "/notes/{note_id}",
    response_model=Note,
    summary="Update an existing note",
    description="Updates the title and/or content of an existing note."
)
async def update_existing_note(note_id: str, note: NoteBase):
    updated_note = update_note(note_id, note.title, note.content)
    if not updated_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID '{note_id}' not found."
        )
    print(f"{Fore.GREEN}INFO: Updated note with ID '{note_id}'.{Style.RESET_ALL}")
    return updated_note

@app.delete(
    "/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a note",
    description="Deletes a note by its unique ID."
)
async def delete_existing_note(note_id: str):
    deleted = delete_note(note_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID '{note_id}' not found."
        )
    return

@app.get(
    "/notes/",
    response_model=List[Note],
    summary="Retrieve all notes",
    description="Returns a list of all notes."
)
async def get_all_notes_endpoint():
    all_notes = get_all_notes()
    print(f"{Fore.BLUE}INFO: Retrieved all {len(all_notes)} notes.{Style.RESET_ALL}")
    return all_notes