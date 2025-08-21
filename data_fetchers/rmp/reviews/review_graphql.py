from data_fetchers.rmp.reviews.configs import REVIEW_LIMIT

def get_school_data_payload(school_name: str) -> dict:
    payload = {
        "query": """
        query SearchSchools($query: SchoolSearchQuery!) {
            newSearch {
                schools(query: $query) {
                    edges {
                        node {
                            id
                            legacyId
                            name
                            city
                            state
                        }
                    }
                }
            }
        }
        """,
        "variables": {
            "query": {
                "text": school_name
            }
        }
    }

    return payload

def get_professors_reviews_payload(professor_id: str):
    payload = {
        "query": f"""
        query GetTeacher($id: ID!) {{
            node(id: $id) {{
                ... on Teacher {{
                    id
                    firstName
                    lastName
                    avgRating
                    numRatings
                    school {{
                        name
                    }}
                    department
                    ratings(first: {REVIEW_LIMIT}) {{
                        edges {{
                            node {{ 
                                id
                                comment
                                class
                                ratingTags
                                date
                                grade
                                difficultyRating
                                helpfulRating
                                isForCredit
                                isForOnlineClass
                            }}
                        }}
                    }}
                    teacherRatingTags {{
                        tagName
                        tagCount
                    }}      
                }}
            }}
        }}
        """, # noqa: E501   
        "variables": {
                "id": professor_id
            }
        }
    return payload

def get_api_schema_payload():
    payload = {
        "query": """
        query {
            __schema {
                types {
                    name
                }
            }
        }
        """
    } 
    return payload