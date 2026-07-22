from typing import Callable
from supabase import Client

from data_fetchers.rmp.ratings.rating_provider import get_ratings_and_merge
from helpers.data import data_keys
from database import courses_db, schools_db, classes_db
from database.schools_db import SchoolStatus
from logger import logger


def run_school_fetch(
    supabase: Client,
    school_name: str,
    rmp_code: str,
    terms_data_list: list,
    get_courses_and_classes: Callable[[], tuple[dict, dict]],
) -> None:
    """
    Shared orchestration for a school's data_fetcher `main()`: saves school/terms data,
    then fetches and saves courses/classes, then marks the school SUPPORTED.
    """
    logger.info("Saving school data to database `schools`.")
    schools_db.save(supabase, school_name, rmp_code, terms_data_list)

    courses_data_table, classes_data_table = get_courses_and_classes()

    logger.info("Saving courses data to database `courses`.")
    courses_db.save(supabase, courses_data_table, school_name)

    _merge_ratings_and_save_classes(supabase, school_name, rmp_code, classes_data_table)

    logger.info(f"Completed fetching. Setting {school_name} status to `supported`.")
    schools_db.set_status(supabase, school_name, SchoolStatus.SUPPORTED.value)


def run_school_fetch_by_terms(
    supabase: Client,
    school_name: str,
    rmp_code: str,
    terms_data_list: list,
    get_courses_and_classes_for_term: Callable[[str], tuple[dict, dict]],
) -> None:
    """
    Variant of `run_school_fetch` that fetches/saves data one term at a time, so a single
    term's failure doesn't lose progress on the others. Saves school/terms data upfront,
    then for each term merges the newly fetched courses data into whatever is already
    stored in `courses` instead of overwriting it (new courses win on conflicting keys),
    then marks the school SUPPORTED once every term is done.
    """
    logger.info("Saving school data to database `schools`.")
    schools_db.save(supabase, school_name, rmp_code, terms_data_list)

    for term_data in terms_data_list:
        term_code = term_data[data_keys.TERM_CODE_KEY]

        courses_data_table, classes_data_table = get_courses_and_classes_for_term(term_code)

        logger.info(f"Merging new courses data for term {term_code} with existing data in database `courses`.")
        existing_courses_data_table = courses_db.get(supabase, school_name)
        merged_courses_data_table = _merge_courses_data_table(existing_courses_data_table, courses_data_table)

        logger.info("Saving courses data to database `courses`.")
        courses_db.save(supabase, merged_courses_data_table, school_name)

        _merge_ratings_and_save_classes(supabase, school_name, rmp_code, classes_data_table)

    logger.info(f"Completed fetching. Setting {school_name} status to `supported`.")
    schools_db.set_status(supabase, school_name, SchoolStatus.SUPPORTED.value)


def _merge_ratings_and_save_classes(supabase: Client, school_name: str, rmp_code: str, classes_data_table: dict) -> None:
    logger.info("Merging ratings data to classes data ...")
    for term_code, classes_all_departments in classes_data_table.items():
        for department_code, classes_one_department in classes_all_departments.items():
            get_ratings_and_merge(supabase, classes_one_department, school_name, rmp_code, department_code)
            logger.info(f"Saving classes data for {department_code} in term {term_code} to database `classes`.")
            classes_db.save_one_entry(supabase, classes_one_department, school_name, term_code, department_code)


def _merge_courses_data_table(existing_courses_data_table: dict, new_courses_data_table: dict) -> dict:
    """
    Combines two `department_code -> [ "COURSE_CODE - Course Title", ... ]` tables,
    keyed by course code, with entries from `new_courses_data_table` taking precedence
    over `existing_courses_data_table` when the same course code appears in both.
    """
    merged_courses_data_table = {}
    for department_code in existing_courses_data_table.keys() | new_courses_data_table.keys():
        courses_by_code = {
            course.split(" - ", 1)[0]: course
            for course in existing_courses_data_table.get(department_code, [])
        }
        courses_by_code.update({
            course.split(" - ", 1)[0]: course
            for course in new_courses_data_table.get(department_code, [])
        })
        merged_courses_data_table[department_code] = list(courses_by_code.values())

    return merged_courses_data_table
