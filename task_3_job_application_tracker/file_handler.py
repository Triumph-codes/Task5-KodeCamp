# task_3_job_application_tracker/file_handler.py

import json
import os
from typing import List, Dict, Any
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# --- Constants ---
DATA_FILE = "applications.json"

def json_serializer(obj):
    """
    Custom JSON serializer to handle objects that are not serializable by default,
    such as datetime objects.
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def load_data() -> List[Dict[str, Any]]:
    """Loads application data from a JSON file."""
    if not os.path.exists(DATA_FILE):
        print(f"{Fore.BLUE}INFO: Application data file '{DATA_FILE}' not found. Starting with an empty list.{Style.RESET_ALL}")
        return []
    
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            print(f"{Fore.GREEN}INFO: Successfully loaded {len(data)} applications from {DATA_FILE}{Style.RESET_ALL}")
            return data
    except (json.JSONDecodeError, IOError) as e:
        print(f"{Fore.RED}ERROR: Could not load data from {DATA_FILE}: {e}. Starting with an empty list.{Style.RESET_ALL}")
        return []

def save_data(data: List[Dict[str, Any]]) -> None:
    """Saves application data to a JSON file."""
    try:
        with open(DATA_FILE, "w") as f:
            # Use the custom serializer to handle datetime objects
            json.dump(data, f, indent=4, default=json_serializer)
        print(f"{Fore.CYAN}INFO: Successfully saved {len(data)} applications to {DATA_FILE}{Style.RESET_ALL}")
    except IOError as e:
        print(f"{Fore.RED}ERROR: Failed to save data to {DATA_FILE}: {e}{Style.RESET_ALL}")