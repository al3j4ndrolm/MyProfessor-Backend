import json
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import the modules
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from data_fetchers.rmp.reviews.reviews import get_reviews, setup_request_session

def test_get_reviews():
    """Test the get_reviews function with a specific professor RMP link"""
    
    # Test parameters
    rmp_link = "professor/89065"
    
    print(f"Testing get_reviews with RMP link: {rmp_link}")
    
    try:
        # Get session
        session = setup_request_session()
        print("✓ Session created successfully")
        
        # Get reviews
        print("Fetching reviews...")
        reviews = get_reviews(rmp_link, session)
        
        if reviews is None:
            print("❌ No reviews returned")
            result = {"error": "No reviews returned", "rmp_link": rmp_link}
        else:
            print("✓ Reviews fetched successfully")
            print(f"Response keys: {list(reviews.keys()) if isinstance(reviews, dict) else 'Not a dict'}")
            
            # Prepare result
            result = {
                "success": True,
                "rmp_link": rmp_link,
                "reviews_data": reviews
            }
            
            # Print some basic info about the response
            if isinstance(reviews, dict) and 'data' in reviews:
                data = reviews['data']
                if 'node' in data and 'ratings' in data['node']:
                    ratings = data['node']['ratings']
                    if 'edges' in ratings:
                        print(f"✓ Found {len(ratings['edges'])} reviews")
                        result["review_count"] = len(ratings['edges'])
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        result = {
            "error": str(e),
            "rmp_link": rmp_link,
        }
    
    # Save result to JSON file
    output_file = "test_reviews_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Results saved to {output_file}")
    return result

if __name__ == "__main__":
    test_get_reviews()
