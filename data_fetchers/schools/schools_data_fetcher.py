import importlib
import os
import sys
import logging
from dotenv import load_dotenv
from supabase import create_client

# Get the path to the schools directory
SCHOOLS_DIR = os.path.dirname(os.path.abspath(__file__))

# List all subdirectories in the schools directory
school_folders = [
    name for name in os.listdir(SCHOOLS_DIR)
    if os.path.isdir(os.path.join(SCHOOLS_DIR, name))
]

# Initialize Supabase client
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

logger = logging.getLogger(__name__)

# Fetch data for each school
logger.info(f'Fetching data for schools...\n\n')
for folder in school_folders:
    main_path = os.path.join(SCHOOLS_DIR, folder, 'main.py')
    if os.path.exists(main_path):
        # Add the school's folder to sys.path so we can import main
        sys.path.insert(0, os.path.join(SCHOOLS_DIR, folder))

        main_module_name = f'data_fetchers.schools.{folder}.main'
        school_config_module_name = f'data_fetchers.schools.{folder}.school_config'

        main_module = importlib.import_module(main_module_name)
        school_config = importlib.import_module(school_config_module_name)
        school_name = getattr(school_config, "SCHOOL_NAME", folder)  # fallback to folder name

        logger.info(f'Start fetching data for {school_name}...')
        try:
            main_module.main(supabase)
            logger.info(f'Finished updating data for {school_name}.\n\n')
        except Exception as e:
            logger.error(f'Error fetching or updating data for {school_name}: {e}\n\n')
            exit(1)
        finally:
            sys.path.pop(0)
    elif not folder.startswith('__'):
        logger.warning(f'Skipping {folder}: no main.py found.\n\n') 