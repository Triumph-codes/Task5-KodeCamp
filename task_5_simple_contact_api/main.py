# task_5_simple_contact_api/main.py

from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel, Field, EmailStr
from typing import Dict, List, Optional
from contextlib import asynccontextmanager
from colorama import Fore, Style, init
import uuid

# Initialize colorama
init(autoreset=True)

# --- In-Memory Data Store ---
# Using a dictionary for O(1) access by ID
contacts_db: Dict[int, Dict] = {}
next_id = 0

# --- Pydantic Models ---
class ContactBase(BaseModel):
    """Base model for creating or updating a contact."""
    name: str = Field(..., min_length=1, description="Full name of the contact")
    email: EmailStr = Field(..., description="Email address of the contact")

class Contact(ContactBase):
    """Full model for a contact, including its unique ID."""
    id: int = Field(..., description="Unique identifier for the contact")

# --- FastAPI App Initialization ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"{Fore.MAGENTA}--- API Startup: Initializing in-memory data store ---{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}WARNING: This API uses an in-memory database. Data will not persist after shutdown.{Style.RESET_ALL}")
    yield
    # Shutdown
    print(f"{Fore.MAGENTA}--- API Shutdown: Data store cleared ---{Style.RESET_ALL}")

app = FastAPI(
    title="Simple Contact API",
    description="An API to manage contact information in-memory.",
    version="1.0.0",
    lifespan=lifespan
)

# --- API Endpoints ---

@app.post(
    "/contacts/",
    response_model=Contact,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new contact",
    description="Adds a new contact to the in-memory database."
)
async def create_contact(contact: ContactBase):
    global next_id
    next_id += 1
    
    new_contact_data = contact.model_dump()
    new_contact_data["id"] = next_id
    contacts_db[next_id] = new_contact_data
    
    print(f"{Fore.GREEN}INFO: New contact created with ID {next_id}.{Style.RESET_ALL}")
    return new_contact_data

@app.get(
    "/contacts/{contact_id}",
    response_model=Contact,
    summary="Retrieve a specific contact",
    description="Returns a single contact by its unique ID."
)
async def get_contact(contact_id: int):
    contact = contacts_db.get(contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with ID {contact_id} not found."
        )
    print(f"{Fore.BLUE}INFO: Retrieved contact with ID {contact_id}.{Style.RESET_ALL}")
    return contact

@app.get(
    "/contacts/search/",
    response_model=List[Contact],
    summary="Search for contacts by name",
    description="Searches for contacts whose names contain the specified query string."
)
async def search_contacts(name: str = Query(..., description="Name to search for")):
    search_results = [
        contact for contact in contacts_db.values() 
        if name.lower() in contact['name'].lower()
    ]
    print(f"{Fore.BLUE}INFO: Search for '{name}' returned {len(search_results)} results.{Style.RESET_ALL}")
    return search_results

@app.put(
    "/contacts/{contact_id}",
    response_model=Contact,
    summary="Update an existing contact",
    description="Updates the name and/or email of a contact by its ID."
)
async def update_contact(contact_id: int, contact_update: ContactBase):
    contact = contacts_db.get(contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with ID {contact_id} not found."
        )
    
    # Update the contact data in the dictionary
    contact.update(contact_update.model_dump())
    
    print(f"{Fore.GREEN}INFO: Updated contact with ID {contact_id}.{Style.RESET_ALL}")
    return contact

@app.delete(
    "/contacts/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a contact",
    description="Deletes a contact by its ID."
)
async def delete_contact(contact_id: int):
    if contact_id not in contacts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with ID {contact_id} not found."
        )
    
    del contacts_db[contact_id]
    
    print(f"{Fore.RED}INFO: Deleted contact with ID {contact_id}.{Style.RESET_ALL}")
    return