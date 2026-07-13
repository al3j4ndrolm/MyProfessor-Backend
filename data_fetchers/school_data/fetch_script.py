import importlib
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
import argparse
import traceback

from data_fetchers.school_data.fetch_config import SCHOOL_FOLDERS

# Get the path to the schools directory
SCHOOLS_DIR = os.path.dirname(os.path.abspath(__file__))

# One error log and one run (start/complete) log per run, under generated/ (gitignored)
REPO_ROOT = os.path.dirname(os.path.dirname(SCHOOLS_DIR))
GENERATED_DIR = os.path.join(REPO_ROOT, "generated")
os.makedirs(GENERATED_DIR, exist_ok=True)
RUN_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
ERROR_LOG_PATH = os.path.join(GENERATED_DIR, f"error_log_{RUN_TIMESTAMP}.log")
RUN_LOG_PATH = os.path.join(GENERATED_DIR, f"run_log_{RUN_TIMESTAMP}.log")


def log_school_error(school_name: str, error_text: str) -> None:
    with open(ERROR_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] School: {school_name}\n{error_text}\n{'-' * 80}\n")


def log_run_event(school_name: str, event: str) -> None:
    with open(RUN_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] School: {school_name} - {event}\n")

# The schools to run, as listed in fetch_config.py
school_folders = SCHOOL_FOLDERS

# Initialize Supabase client
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

logger = logging.getLogger(__name__)

# Argument parsing for target_tables and schools
parser = argparse.ArgumentParser(description="Fetch and update data for schools.")
parser.add_argument(
    "--tables",
    type=str,
    default=None,
    help="Comma-separated list of tables to update (e.g., courses,classes,professors,schools). If omitted, all tables will be updated."
)
parser.add_argument(
    "--schools",
    type=str,
    default=None,
    help="Comma-separated list of school folder names to process (e.g., de_anza_college,sjsu). If omitted, all schools will be processed."
)
args = parser.parse_args()

if args.tables:
    target_tables = set([t.strip() for t in args.tables.split(",") if t.strip()])
    logger.info(f"Target tables specified: {target_tables}")
else:
    target_tables = {"courses", "classes", "professors", "schools"}
    logger.info("No target tables specified. All tables will be updated.")

if args.schools:
    selected_schools = set([s.strip() for s in args.schools.split(",") if s.strip()])
    logger.info(f"Running only for specified schools: {selected_schools}")
    filtered_school_folders = [folder for folder in school_folders if folder in selected_schools]
else:
    filtered_school_folders = school_folders
    logger.info("No specific schools specified. All schools will be processed.")

# Fetch data for each school
logger.info(f'Fetching data for schools...\n\n')
for folder in filtered_school_folders:
    main_path = os.path.join(SCHOOLS_DIR, folder, 'main.py')
    if os.path.exists(main_path):
        # Add the school's folder to sys.path so we can import main
        sys.path.insert(0, os.path.join(SCHOOLS_DIR, folder))

        main_module_name = f'data_fetchers.school_data.{folder}.main'
        school_config_module_name = f'data_fetchers.school_data.{folder}.school_config'

        main_module = importlib.import_module(main_module_name)
        school_config = importlib.import_module(school_config_module_name)
        school_name = getattr(school_config, "SCHOOL_NAME", folder)  # fallback to folder name

        logger.info(f'Start fetching data for {school_name}...')
        log_run_event(school_name, "STARTED")
        try:
            import inspect
            main_sig = inspect.signature(main_module.main)
            if len(main_sig.parameters) == 2:
                main_module.main(supabase, target_tables)
            else:
                main_module.main(supabase, {"courses", "classes", "professors", "schools"})
            logger.info(f'Finished updating data for {school_name}.\n\n')
            log_run_event(school_name, "COMPLETED")
        except Exception as e:
            error_text = traceback.format_exc()
            logger.error(f'Error fetching or updating data for {school_name}: {error_text}\n\n')
            log_school_error(school_name, error_text)
            log_run_event(school_name, "FAILED")
        finally:
            sys.path.pop(0)
    elif not folder.startswith('__'):
        logger.warning(f'Skipping {folder}: no main.py found.\n\n') 