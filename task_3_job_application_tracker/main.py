# task_3_job_application_tracker/main.py

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import enum
from datetime import datetime
from contextlib import asynccontextmanager
from colorama import Fore, Style, init

from file_handler import load_data, save_data

# Initialize colorama
init(autoreset=True)

# --- In-Memory Data Store ---
# This will be loaded from JSON on startup
applications_db: List[Dict] = []
next_id = 0

# --- Pydantic Models ---
class ApplicationStatus(str, enum.Enum):
    """Enumeration for valid job application statuses."""
    pending = "Pending"
    interviewing = "Interviewing"
    rejected = "Rejected"
    accepted = "Accepted"

class JobApplicationBase(BaseModel):
    """Base model for creating a new job application."""
    company: str = Field(..., min_length=1, description="Name of the company")
    title: str = Field(..., min_length=1, description="Job title")
    status: ApplicationStatus = Field(ApplicationStatus.pending, description="Status of the application")

class JobApplication(JobApplicationBase):
    """Full model for a job application, including generated fields."""
    id: int = Field(..., gt=0, description="Unique identifier for the application")
    date_applied: datetime = Field(
        default_factory=datetime.now, 
        description="Date and time the application was submitted"
    )
    
    # Validator to ensure that id is correctly generated
    @staticmethod
    def generate_id():
        global next_id
        current_id = next_id
        next_id += 1
        return current_id

# --- FastAPI App Initialization ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    global applications_db, next_id
    print(f"{Fore.MAGENTA}--- API Startup: Loading data ---{Style.RESET_ALL}")
    
    # Load data from file
    loaded_data = load_data()
    applications_db.extend(loaded_data)
    
    # Set next_id to be one greater than the highest existing ID
    if applications_db:
        next_id = max(app['id'] for app in applications_db) + 1
    else:
        next_id = 1
        
    print(f"{Fore.GREEN}INFO: Ready. Next application ID will be {next_id}.{Style.RESET_ALL}")
    
    yield
    
    print(f"{Fore.MAGENTA}--- API Shutdown ---{Style.RESET_ALL}")
    save_data(applications_db)

app = FastAPI(
    title="Job Application Tracker API",
    description="API for tracking job applications.",
    version="1.0.0",
    lifespan=lifespan
)

# --- API Endpoints ---

@app.post(
    "/applications/",
    response_model=JobApplication,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job application",
    description="Adds a new job application to the tracker."
)
async def create_application(application_data: JobApplicationBase):
    global applications_db, next_id
    
    new_application = JobApplication(
        id=next_id,
        company=application_data.company,
        title=application_data.title,
        status=application_data.status
    )
    
    applications_db.append(new_application.model_dump())
    save_data(applications_db)
    
    # Increment the next ID for the next application
    next_id += 1
    
    print(f"{Fore.GREEN}INFO: New application created for '{new_application.company}' with ID {new_application.id}.{Style.RESET_ALL}")
    return new_application

@app.get(
    "/applications/",
    response_model=List[JobApplication],
    summary="Retrieve all job applications",
    description="Returns a list of all tracked job applications."
)
async def get_all_applications():
    print(f"{Fore.BLUE}INFO: Retrieved all {len(applications_db)} applications.{Style.RESET_ALL}")
    return applications_db

@app.get(
    "/applications/{app_id}",
    response_model=JobApplication,
    summary="Retrieve a specific job application",
    description="Returns a job application by its unique ID."
)
async def get_application_by_id(app_id: int):
    application = next((app for app in applications_db if app['id'] == app_id), None)
    
    if application is None:
        print(f"{Fore.YELLOW}WARNING: Application with ID {app_id} not found.{Style.RESET_ALL}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {app_id} not found."
        )
    
    print(f"{Fore.BLUE}INFO: Retrieved application with ID {app_id}.{Style.RESET_ALL}")
    return application