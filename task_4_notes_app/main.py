# task_4_notes_app/main.py

from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from uuid import UUID
from contextlib import asynccontextmanager
from colorama import Fore, Style, init

from file_storage import setup_directory, create_note, get_note, save_note_update, delete_note, get_all_notes

# Initialize colorama
init(autoreset=True)

# --- Pydantic Models ---
class NoteBase(BaseModel):
    """Base model for a note."""
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)

class Note(NoteBase):
    """Full model for a note, including its unique ID."""
    id: str

class NoteUpdate(BaseModel):
    """Model for partial updates to a note."""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[str] = Field(None, min_length=1)

# --- FastAPI App Initialization ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"{Fore.MAGENTA}--- API Startup: Setting up storage ---{Style.RESET_ALL}")
    setup_directory()
    yield
    print(f"{Fore.MAGENTA}--- API Shutdown ---{Style.RESET_ALL}")

app = FastAPI(
    title="Notes App API",
    description="An API to manage notes, with each note stored as a file.",
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
async def create_note_endpoint(note_data: NoteBase):
    new_note = create_note(note_data.model_dump())
    return new_note

@app.get(
    "/notes/",
    response_model=List[Note],
    summary="Retrieve all notes",
    description="Retrieves a list of all notes from the file system."
)
async def get_all_notes_endpoint():
    notes = get_all_notes()
    print(f"{Fore.BLUE}INFO: Retrieved {len(notes)} notes.{Style.RESET_ALL}")
    return notes

@app.get(
    "/notes/search/",
    response_model=List[Note],
    summary="Search for notes",
    description="Searches for notes whose title or content contains the query string."
)
async def search_notes(q: str = Query(..., min_length=1, description="Search term for note title or content")):
    notes = get_all_notes()
    found_notes = [
        note for note in notes
        if q.lower() in note['title'].lower() or q.lower() in note['content'].lower()
    ]
    print(f"{Fore.BLUE}INFO: Found {len(found_notes)} notes matching query '{q}'.{Style.RESET_ALL}")
    return found_notes

@app.get(
    "/notes/{note_id}",
    response_model=Note,
    summary="Retrieve a specific note",
    description="Retrieves a single note by its unique ID."
)
async def get_note_by_id(note_id: str):
    note = get_note(note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID {note_id} not found."
        )
    print(f"{Fore.BLUE}INFO: Retrieved note with ID: {note_id}{Style.RESET_ALL}")
    return note

@app.patch(
    "/notes/{note_id}",
    response_model=Note,
    summary="Partially update a note",
    description="Updates one or more fields of an existing note. You can change either the title or the entire content, or both."
)
async def partial_update_note(note_id: str, update_data: NoteUpdate):
    existing_note = get_note(note_id)
    if not existing_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID {note_id} not found."
        )
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        existing_note[key] = value
        
    updated_note = save_note_update(note_id, existing_note)
    if not updated_note: 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save note after update."
        )
    
    print(f"{Fore.GREEN}INFO: Partially updated note with ID: {note_id}{Style.RESET_ALL}")
    return updated_note

@app.put(
    "/notes/{note_id}",
    response_model=Note,
    summary="Update a note (full replacement)",
    description="Replaces an entire note with the new data."
)
async def update_note_endpoint(note_id: str, updated_data: NoteBase):
    existing_note = get_note(note_id)
    if not existing_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID {note_id} not found."
        )
    
    updated_note = {**updated_data.model_dump(), "id": note_id}
    updated_note_saved = save_note_update(note_id, updated_note)
    
    if not updated_note_saved:
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save note after update."
        )

    return updated_note_saved

@app.delete(
    "/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a note",
    description="Deletes a note by its unique ID."
)
async def delete_note_endpoint(note_id: str):
    if not delete_note(note_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID {note_id} not found."
        )
    return None