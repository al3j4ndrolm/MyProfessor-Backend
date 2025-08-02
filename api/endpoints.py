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
from database import courses_db, classes_db, professors_db, db_keys, reports_db
from helpers.data import data_creators

# Initialize FastAPI app and router
app = FastAPI()
router = APIRouter()

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

class StartPostRequest(BaseModel):
    '''
    client_data = {
        "build_type": "dev" | "release",
        "platform": "iOS" | "Android"
    }
    user_data = {
        "is_new_user": "true" | "false"
    }
    '''
    client_data: dict
    user_data: dict

@router.post("/start")
def start_post(
    body: StartPostRequest = Body(...)
):
    if not body.client_data or not body.user_data:
        raise HTTPException(status_code=400)

    if body.client_data.get("build_type") is None or body.client_data.get("platform") is None:
        raise HTTPException(status_code=400)

    if body.user_data.get("is_new_user") is None:
        raise HTTPException(status_code=400)
    
    return response.response_start(supabase, body.client_data, body.user_data)

@router.get("/courses")
def courses_get(
    school: str = None
):
    if school is None:
        raise HTTPException(status_code=400)
    else:
        return courses_db.get(supabase, school)

@router.get("/classes")
def classes_get(
    school: str = None,
    term: str = None,
    department: str = None
):
    if school is None or term is None or department is None:
        raise HTTPException(status_code=400)
    else:
        return classes_db.get_one_entry(supabase, school, term, department)

class ReportsErrorsPostRequest(BaseModel):
    critical: bool
    details: str
    platform: str
    build: str
    version: str

@router.post("/reports/errors")
def reports_errors_post(
    body: ReportsErrorsPostRequest = Body(...)
):
    reports_db.save(supabase, body, is_error=True)

# TODO: Remove after client migrates to new classes endpoints
@router.get("/schools/")
@router.get("/schools")
def schools_get():
    return response.response_schools(supabase)

# TODO: Remove after client migrates to new classes endpoints
class ClassesPostRequest(BaseModel):
    school: str
    term: str
    department: str

# TODO: Remove after client migrates to new classes endpoints
@deprecated
@router.post("/professors/schedules/")
@router.post("/professors/schedules")
def classes_post(
    body: ClassesPostRequest = Body(...)
):
    if not body.school or not body.term or not body.department:
        raise HTTPException(status_code=400)

    classes_data = classes_db.get_one_entry(supabase, body.school, body.term, body.department)
    
    return_data = {}
    for course_code, classes_one_course in classes_data.items():
        return_data[course_code] = {}
        for professor_identifier, professor_data in classes_one_course.items():
            professor_name, professor_email = data_creators.parse_professor_identifier(professor_identifier)
            return_data[course_code][professor_name] = professor_data
            
    return return_data

# TODO: Remove after client migrates to new classes endpoints
class ProfessorsPostRequest(BaseModel):
    school: str
    department: str
    professors: list[str]

# TODO: Remove after client migrates to new classes endpoints
@deprecated
@router.post("/professors/ratings/")
@router.post("/professors/ratings")
def ratings_post(
    body: ProfessorsPostRequest = Body(...)
):
    if not body.school or not body.department or not body.professors:
        raise HTTPException(status_code=400)

    response = {}
    for professor_name in body.professors:
        professor_entry = professors_db.get_without_email(supabase, body.school, body.department, professor_name)
        if professor_entry:
            rating = professor_entry[db_keys.KEY_RMP_RATING] if professor_entry[db_keys.KEY_RMP_RATING] is not None else -0.1
            difficulty = professor_entry[db_keys.KEY_RMP_DIFFICULTY] if professor_entry[db_keys.KEY_RMP_DIFFICULTY] is not None else 5.1
            recommend = professor_entry[db_keys.KEY_RMP_RECOMMEND] if professor_entry[db_keys.KEY_RMP_RECOMMEND] is not None else -1
            review_count = professor_entry[db_keys.KEY_RMP_REVIEWS_COUNT] if professor_entry[db_keys.KEY_RMP_REVIEWS_COUNT] is not None else 0

            response[professor_name] = {
                "overallRating": rating,
                "difficulty": difficulty,
                "wouldTakeAgain": recommend,
                "ratingsQuantity": review_count
            }
        else:
            response[professor_name] = {
                "overallRating": -0.1,
                "difficulty": 5.1,
                "wouldTakeAgain": -1,
                "ratingsQuantity": 0
            }

    return response

app.include_router(router)
