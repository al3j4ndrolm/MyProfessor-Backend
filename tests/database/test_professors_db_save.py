import os
import sys
from supabase import create_client, Client
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.professors_db import save_one_entry, get_one_entry
from database import db_keys
from helpers.data.data_keys import (
    PROFESSOR_RATING_KEY,
    PROFESSOR_DIFFICULTY_KEY,
    PROFESSOR_RECOMMEND_KEY,
    PROFESSOR_REVIEW_COUNT_KEY,
    PROFESSOR_SCORE_KEY,
    PROFESSOR_LINK_KEY
)

def test_save_professor_with_timestamp():
    """
    Test function to save a test professor and verify that Supabase creates timestamps.
    This will help us see if the created_at and updated_at fields are automatically set.
    """
    
    # Initialize Supabase client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY environment variables are required")
        print("Please set these environment variables before running the test")
        return
    
    supabase = create_client(url, key)
    
    # Test data
    test_school = "Test University"
    test_department = "Computer Science"
    test_professor_name = "Dr. Test Professor"
    test_professor_email = "test.professor@testuniversity.edu"
    
    # Mock RMP data
    test_rmp_data = {
        PROFESSOR_RATING_KEY: 4.5,
        PROFESSOR_DIFFICULTY_KEY: 3.2,
        PROFESSOR_RECOMMEND_KEY: 95,
        PROFESSOR_REVIEW_COUNT_KEY: 42,
        PROFESSOR_SCORE_KEY: 4.3,
        PROFESSOR_LINK_KEY: "https://www.ratemyprofessors.com/professor/test"
    }
    
    print(f"🧪 Testing save_one_entry function...")
    print(f"📝 Test data:")
    print(f"   School: {test_school}")
    print(f"   Department: {test_department}")
    print(f"   Professor: {test_professor_name}")
    print(f"   Email: {test_professor_email}")
    print(f"   RMP Rating: {test_rmp_data[PROFESSOR_RATING_KEY]}")
    print(f"   RMP Difficulty: {test_rmp_data[PROFESSOR_DIFFICULTY_KEY]}")
    
    try:
        # Save the test professor
        print(f"\n💾 Saving test professor to Supabase...")
        save_one_entry(supabase, test_school, test_department, test_professor_name, test_professor_email, test_rmp_data)
        print(f"✅ Professor saved successfully!")
        
        # Retrieve the saved professor to check timestamps
        print(f"\n🔍 Retrieving saved professor to check timestamps...")
        saved_professor = get_one_entry(supabase, test_school, test_department, test_professor_name, test_professor_email)
        
        if saved_professor:
            print(f"✅ Professor retrieved successfully!")
            print(f"\n📊 Professor data:")
            print(f"   Name: {saved_professor[db_keys.KEY_PROFESSOR_NAME]}")
            print(f"   Email: {saved_professor[db_keys.KEY_EMAIL]}")
            print(f"   School: {saved_professor[db_keys.KEY_SCHOOL]}")
            print(f"   Department: {saved_professor[db_keys.KEY_DEPARTMENT]}")
            print(f"   RMP Rating: {saved_professor[db_keys.KEY_RMP_RATING]}")
            print(f"   RMP Difficulty: {saved_professor[db_keys.KEY_RMP_DIFFICULTY]}")
            print(f"   RMP Recommend: {saved_professor[db_keys.KEY_RMP_RECOMMEND]}")
            print(f"   RMP Reviews Count: {saved_professor[db_keys.KEY_RMP_REVIEWS_COUNT]}")
            print(f"   RMP Score: {saved_professor[db_keys.KEY_RMP_SCORE]}")
            print(f"   RMP Link: {saved_professor[db_keys.KEY_RMP_LINK]}")
            
            # Check if timestamps exist in the raw data
            print(f"\n⏰ Checking for timestamps...")
            print(f"📋 Raw data keys: {list(saved_professor.keys())}")
            
            # Check for timestamp fields
            timestamp_fields = ["updated_at", "id"]
            for field in timestamp_fields:
                if field in saved_professor:
                    print(f"   ✅ {field}: {saved_professor[field]}")
                else:
                    print(f"   ❌ {field}: Not found")
            
            # Check if timestamps are automatically set
            if "updated_at" in saved_professor and saved_professor["updated_at"]:
                print(f"\n🎉 SUCCESS: Supabase automatically created timestamp!")
                print(f"   Updated at: {saved_professor['updated_at']}")
            else:
                print(f"   ⚠️  WARNING: No updated_at timestamp found")
                
        else:
            print(f"❌ Failed to retrieve the saved professor")
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_save_professor_with_timestamp() 