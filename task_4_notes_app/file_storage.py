# task_4_notes_app/file_storage.py

import os
import json
import uuid
from typing import Dict, List, Optional, Any
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# --- Constants ---
NOTES_DIR = "notes"

def setup_directory() -> None:
    """Ensures the notes directory exists."""
    if not os.path.exists(NOTES_DIR):
        os.makedirs(NOTES_DIR)
        print(f"{Fore.GREEN}INFO: Created '{NOTES_DIR}' directory.{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}INFO: Directory '{NOTES_DIR}' already exists.{Style.RESET_ALL}")

def _get_file_path(note_id: str) -> str:
    """Returns the full path for a note file."""
    return os.path.join(NOTES_DIR, f"{note_id}.json")

def create_note(note_data: Dict) -> Dict:
    """Creates a new note file and returns the note data."""
    setup_directory()
    note_id = str(uuid.uuid4())
    note_data['id'] = note_id
    file_path = _get_file_path(note_id)
    
    try:
        with open(file_path, "w") as f:
            json.dump(note_data, f, indent=4)
        print(f"{Fore.CYAN}INFO: Created note with ID '{note_id}' at '{file_path}'.{Style.RESET_ALL}")
        return note_data
    except IOError as e:
        print(f"{Fore.RED}ERROR: Failed to create note file: {e}{Style.RESET_ALL}")
        raise IOError(f"Failed to create note file: {e}")

def get_note(note_id: str) -> Optional[Dict]:
    """Retrieves a note by its ID."""
    file_path = _get_file_path(note_id)
    if not os.path.exists(file_path):
        print(f"{Fore.YELLOW}WARNING: Note file for ID '{note_id}' not found.{Style.RESET_ALL}")
        return None
    
    try:
        with open(file_path, "r") as f:
            note_data = json.load(f)
        return note_data
    except (IOError, json.JSONDecodeError) as e:
        print(f"{Fore.RED}ERROR: Failed to read note file '{note_id}': {e}{Style.RESET_ALL}")
        return None

def save_note_update(note_id: str, updated_data: Dict) -> Optional[Dict]:
    """Updates an existing note file."""
    file_path = _get_file_path(note_id)
    if not os.path.exists(file_path):
        print(f"{Fore.YELLOW}WARNING: Note with ID '{note_id}' not found for update.{Style.RESET_ALL}")
        return None
        
    try:
        with open(file_path, "w") as f:
            json.dump(updated_data, f, indent=4)
        print(f"{Fore.CYAN}INFO: Updated note with ID '{note_id}'.{Style.RESET_ALL}")
        return updated_data
    except IOError as e:
        print(f"{Fore.RED}ERROR: Failed to update note file: {e}{Style.RESET_ALL}")
        raise IOError(f"Failed to update note file: {e}")

def delete_note(note_id: str) -> bool:
    """Deletes a note file."""
    file_path = _get_file_path(note_id)
    if not os.path.exists(file_path):
        print(f"{Fore.YELLOW}WARNING: Attempted to delete non-existent note with ID '{note_id}'.{Style.RESET_ALL}")
        return False
        
    try:
        os.remove(file_path)
        print(f"{Fore.GREEN}INFO: Deleted note file with ID '{note_id}'.{Style.RESET_ALL}")
        return True
    except OSError as e:
        print(f"{Fore.RED}ERROR: Failed to delete note file '{note_id}': {e}{Style.RESET_ALL}")
        return False

def get_all_notes() -> List[Dict[str, Any]]:
    """Retrieves all notes from the notes directory."""
    notes = []
    setup_directory()
    try:
        for filename in os.listdir(NOTES_DIR):
            if filename.endswith(".json"):
                note_id = os.path.splitext(filename)[0]
                note_data = get_note(note_id)
                if note_data:
                    notes.append(note_data)
        return notes
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"{Fore.RED}ERROR: An unexpected error occurred while listing notes: {e}{Style.RESET_ALL}")
        return []