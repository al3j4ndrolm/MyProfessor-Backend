# External imports
from fastapi.exceptions import HTTPException
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, Body
from pydantic import BaseModel

# Local imports
from api import response
from database import courses_db, classes_db

# Initialize FastAPI app and router
app = FastAPI()
router = APIRouter()

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

class ClassesPostRequest(BaseModel):
    school: str
    term: str
    department: str

@router.get("/schools")
def schools_get():
    return response.response_schools(supabase)

@router.get("/courses")
def courses_get(
    school_name: str = None
):
    if school_name is None:
        raise HTTPException(status_code=400, detail="Missing school name")
    else:
        return courses_db.get(supabase, school_name)

@router.get("/classes")
def classes_get(
    school_name: str = None,
    term: str = None,
    department: str = None
):
    if school_name is None:
        raise HTTPException(status_code=400, detail="Missing school name")
    elif term is None:
        raise HTTPException(status_code=400, detail="Missing term")
    elif department is None:
        raise HTTPException(status_code=400, detail="Missing department")
    else:
        return classes_db.get(supabase, school_name, term, department)

@router.post("/professors/schedules")
def classes_post(
    body: ClassesPostRequest = Body(...)
):
    # Validate required fields
    if not body.school:
        raise HTTPException(status_code=400, detail="Missing school name in request body")
    elif not body.term:
        raise HTTPException(status_code=400, detail="Missing term in request body")
    elif not body.department:
        raise HTTPException(status_code=400, detail="Missing department in request body")

    return classes_db.get(supabase, body.school, body.term, body.department)

app.include_router(router)
