# External imports
from deprecation import deprecated
from fastapi.exceptions import HTTPException
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, Body
from pydantic import BaseModel

# Local imports
from api import response
from database import courses_db, classes_db, professors_db

# Initialize FastAPI app and router
app = FastAPI()
router = APIRouter()

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

@router.get("/schools")
def schools_get():
    return response.response_schools(supabase)

@router.get("/courses")
def courses_get(
    school: str = None
):
    if school is None:
        raise HTTPException(status_code=400, detail="Missing school name")
    else:
        return courses_db.get(supabase, school)

@router.get("/classes")
def classes_get(
    school: str = None,
    term: str = None,
    department: str = None
):
    if school is None:
        raise HTTPException(status_code=400, detail="Missing school name")
    elif term is None:
        raise HTTPException(status_code=400, detail="Missing term")
    elif department is None:
        raise HTTPException(status_code=400, detail="Missing department")
    else:
        return response.response_classes(supabase, school, term, department)

# Remove after client migrates to new classes endpoints
class ClassesPostRequest(BaseModel):
    school: str
    term: str
    department: str

# Remove after client migrates to new classes endpoints
@deprecated
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

# Remove after client migrates to new classes endpoints
class ProfessorsPostRequest(BaseModel):
    school: str
    department: str
    professors: list[str]

# Remove after client migrates to new classes endpoints
@deprecated
@router.post("/professors/ratings")
def ratings_post(
    body: ProfessorsPostRequest = Body(...)
):
    if not body.school:
        raise HTTPException(status_code=400, detail="Missing school name in request body")
    elif not body.department:
        raise HTTPException(status_code=400, detail="Missing department in request body")
    elif not body.professors:
        raise HTTPException(status_code=400, detail="Missing professor names in request body")

    response = {}
    for professor_name in body.professors:
        professor_data = professors_db.get_without_email(supabase, body.school, body.department, professor_name)

        rating = professor_data["rating"] if professor_data and professor_data["rating"] else -0.1
        difficulty = professor_data["difficulty"] if professor_data and professor_data["difficulty"] else 5.1
        recommend = professor_data["recommend"] if professor_data and professor_data["recommend"] else -1
        review_count = professor_data["review_count"] if professor_data and professor_data["review_count"] else 0

        response[professor_name] = {
            "overallRating": rating,
            "difficulty": difficulty,
            "wouldTakeAgain": recommend,
            "ratingsQuantity": review_count
        }

    return response

app.include_router(router)
