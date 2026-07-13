from typing import Callable
from supabase import Client

from data_fetchers.rmp.ratings.rating_provider import get_ratings_and_merge
from database import courses_db, schools_db, classes_db
from database.schools_db import SchoolStatus
from logger import logger


def run_school_fetch(
    supabase: Client,
    target_tables: set[str],
    school_name: str,
    rmp_code: str,
    terms_data_list: list,
    get_courses_and_classes: Callable[[], tuple[dict, dict]],
) -> None:
    """
    Shared orchestration for a school's data_fetcher `main()`: saves school/terms data,
    then (if requested) fetches and saves courses/classes, then marks the school SUPPORTED.
    `get_courses_and_classes` is called lazily, only if courses or classes are requested.
    """
    if "schools" in target_tables:
        logger.info("Saving school data to database `schools`.")
        schools_db.save(supabase, school_name, rmp_code, terms_data_list)

    if "courses" in target_tables or "classes" in target_tables:
        courses_data_table, classes_data_table = get_courses_and_classes()

        if "courses" in target_tables:
            logger.info("Saving courses data to database `courses`.")
            courses_db.save(supabase, courses_data_table, school_name)

        if "classes" in target_tables:
            logger.info("Merging ratings data to classes data ...")
            for term_code, classes_all_departments in classes_data_table.items():
                for department_code, classes_one_department in classes_all_departments.items():
                    get_ratings_and_merge(supabase, classes_one_department, school_name, rmp_code, department_code)
                    logger.info(f"Saving classes data for {department_code} in term {term_code} to database `classes`.")
                    classes_db.save_one_entry(supabase, classes_one_department, school_name, term_code, department_code)

    logger.info(f"Completed fetching. Setting {school_name} status to `supported`.")
    schools_db.set_status(supabase, school_name, SchoolStatus.SUPPORTED.value)
