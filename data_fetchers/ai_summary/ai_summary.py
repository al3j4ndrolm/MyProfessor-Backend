#!/usr/bin/env python3
# Minimal: RMP -> DeepSeek -> JSON:
# {
#   "popularTags": [string],
#   "recentCourseFeedback": { "<COURSE>": "<paragraph>" },
#   "strengths": [string],
#   "challenges": [string],
#   "finalTake": string
# }

import base64, json, random, time
from typing import Dict, List, Optional
import requests
from statistics import mean
from supabase import Client
from logger import logger
from data_fetchers.ai_summary.ai_summary_configs import RMP_ENDPOINT, DEEPSEEK_BASE, DEEPSEEK_MODEL, HEADER, DEEPSEEK_API_KEY, QUERY_SUMMARY
from data_fetchers.ratings.rating_provider import db_keys

S = requests.Session()
S.headers.update(HEADER)

# Try a few field-name combos to stay short but robust
COURSE_FIELDS = ["courseCode","class","courseName","course","className","courseType"]
ONLINE_FIELDS = ["isForOnlineClass","isOnline","onlineClass"]

# ============================================================================
# PUBLIC FUNCTIONS
# ============================================================================

def generate_ai_summary(supabase: Client, professor_name: str, school: str, professor_email: str, rmp_link: str = None) -> Optional[Dict]:
    """
    Generate AI summary for a professor using their RMP data.
    
    Args:
        professor_name: Name of the professor
        school: School name
        professor_email: Professor's email
        rmp_link: RMP link (optional, will be extracted from RMP if not provided)
    
    Returns:
        AI summary dict or None if generation fails
    """
    try:
        # Get school RMP code from database
        if not supabase:
            logger.error("Supabase client not initialized. Cannot generate AI summary.")
            return None
        
        # Get school info to find RMP code
        school_result = supabase.table("schools").select(db_keys.SCHOOL_KEY_RMP_CODE).eq("school", school).execute()
        if not school_result.data:
            logger.warning(f"School {school} not found in database. Cannot generate AI summary for {professor_name}.")
            return None
        
        rmp_code = school_result.data[0]["rmp_code"]
        
        # Find teacher ID from RMP
        teacher_id = None
        if rmp_link:
            # Extract teacher ID from RMP link if provided
            import re
            match = re.search(r'/professor/(\d+)', rmp_link)
            if match:
                teacher_id = b64_node("Teacher", int(match.group(1)))
        
        if not teacher_id:
            # Try to find teacher by name and school
            teacher_id = find_teacher(professor_name, int(rmp_code))
        
        if not teacher_id:
            logger.warning(f"Could not find RMP teacher ID for {professor_name} at {school}. Cannot generate AI summary.")
            return None
        
        # Fetch reviews
        reviews = fetch_reviews(teacher_id, max_reviews=200)
        if not reviews:
            logger.warning(f"No reviews found for {professor_name}. Cannot generate AI summary.")
            return None
        
        # Build hints and generate summary
        hints = build_hints(reviews)
        api_key = DEEPSEEK_API_KEY
        if not api_key:
            logger.error("DEEPSEEK_API_KEY not found in environment. Cannot generate AI summary.")
            return None
        
        summary = deepseek_min_json(reviews, hints, api_key)
        
        logger.info(f"Successfully generated AI summary for {professor_name}")
        return summary
            
    except Exception as e:
        logger.error(f"Error generating AI summary for {professor_name}: {e}")
        return None

# ============================================================================
# PRIVATE FUNCTIONS (internal helpers, ordered by call order)
# ============================================================================

def execute_rmp_graphql_query(query: str, variables: Optional[Dict] = None) -> Dict:
    """Execute GraphQL query against RateMyProfessors API."""
    time.sleep(random.uniform(0.2, 0.5))
    r = S.post(RMP_ENDPOINT, json={"query": query, "variables": variables or {}}, timeout=30)
    r.raise_for_status()
    j = r.json()
    if j.get("errors"):
        raise RuntimeError(json.dumps(j["errors"]))
    return j["data"]

def b64_node(type_name: str, legacy_id: int) -> str:
    """Create base64 encoded node ID for GraphQL queries."""
    return base64.b64encode(f"{type_name}-{legacy_id}".encode()).decode()

def find_teacher(name: str, school_legacy_id: int) -> Optional[str]:
    """Find teacher ID from RMP using name and school."""
    q = """
    query($q: TeacherSearchQuery!){
      newSearch{ teachers(query:$q){ edges{ node{ id } } } }
    }"""
    gid = b64_node("School", school_legacy_id)
    d = execute_rmp_graphql_query(q, {"q": {"text": name, "schoolID": gid, "fallback": True}})
    edges = d.get("newSearch", {}).get("teachers", {}).get("edges", [])
    return edges[0]["node"]["id"] if edges else None

def fetch_reviews(teacher_id: str, page_size=25, max_reviews=180) -> List[Dict]:
    """Fetch reviews for a teacher from RMP."""
    base_fields = ["comment","qualityRating","difficultyRating","ratingTags","grade"]
    after = None
    out = []

    def try_query(course_field: Optional[str], online_field: Optional[str]) -> str:
        flds = base_fields.copy()
        if course_field: flds.append(course_field)
        if online_field: flds.append(online_field)
        sel = "\n              ".join(flds)
        return f"""
        query($id:ID!, $first:Int, $after:String){{
          node(id:$id){{
            ... on Teacher{{
              ratings(first:$first, after:$after){{
                pageInfo{{hasNextPage endCursor}}
                edges{{ node{{ {sel} }} }}
              }}
            }}
          }}
        }}"""

    # try combos quickly; if a query fails, move to the next combo
    combos = [(c, o) for c in COURSE_FIELDS for o in ONLINE_FIELDS] + [(None, None)]
    for cfield, ofield in combos:
        try:
            after = None
            out = []
            while len(out) < max_reviews:
                d = execute_rmp_graphql_query(try_query(cfield, ofield), {"id": teacher_id, "first": page_size, "after": after})
                r = (d.get("node") or {}).get("ratings") or {}
                out.extend(e["node"] for e in r.get("edges", []))
                if not r.get("pageInfo", {}).get("hasNextPage"): break
                after = r["pageInfo"]["endCursor"]
            # success for this combo
            return normalize_reviews(out, cfield, ofield)[:max_reviews]
        except Exception:
            continue
    # last resort: minimal fields only
    return normalize_reviews(out, None, None)[:max_reviews]

def _to_bool(v):
    """Convert value to boolean."""
    if isinstance(v, bool): return v
    if isinstance(v, (int, float)): return bool(v)
    if isinstance(v, str): return v.strip().lower() in ("true","1","yes","y")
    return None

def _norm_course(v) -> Optional[str]:
    """Normalize course field value."""
    if v is None: return None
    s = str(v).strip()
    return None if (not s or s.isdigit()) else s

def _norm_tags(v) -> List[str]:
    """Normalize tags field value."""
    if v is None: return []
    if isinstance(v, list): return [str(x).strip() for x in v if str(x).strip()]
    return [p.strip() for p in str(v).split("--") if p.strip()]

def normalize_reviews(rows: List[Dict], course_field: Optional[str], online_field: Optional[str]) -> List[Dict]:
    """Normalize review data from RMP."""
    out = []
    for r in rows:
        out.append({
            "quality": r.get("qualityRating"),
            "difficulty": r.get("difficultyRating"),
            "review": r.get("comment"),
            "grade": r.get("grade"),
            "online": _to_bool(r.get(online_field)) if online_field else None,
            "course": _norm_course(r.get(course_field)) if course_field else None,
            "tags": _norm_tags(r.get("ratingTags")),
        })
    return out

def build_hints(reviews: List[Dict]) -> Dict:
    """Build hints from reviews for AI summary generation."""
    # top tags with counts
    tag_counts: Dict[str, int] = {}
    for r in reviews:
        for t in r.get("tags", []):
            tag_counts[t] = tag_counts.get(t, 0) + 1
    popular_tags = [{"tag": t, "mentions": c} for t, c in sorted(tag_counts.items(), key=lambda kv: -kv[1])[:8]]
    
    # top courses
    course_counts: Dict[str, int] = {}
    for r in reviews:
        c = r.get("course")
        if c: course_counts[c] = course_counts.get(c, 0) + 1
    top_courses = [c for c, _ in sorted(course_counts.items(), key=lambda kv: -kv[1])[:4]]
    
    # calculate averages
    q = [r["quality"] for r in reviews if isinstance(r.get("quality"), (int, float))]
    d = [r["difficulty"] for r in reviews if isinstance(r.get("difficulty"), (int, float))]
    
    # calculate would take again percentage (assuming grade A-C means would take again)
    would_take_again = 0
    total_grades = 0
    for r in reviews:
        grade = r.get("grade")
        if grade and isinstance(grade, str):
            grade_upper = grade.upper()
            if grade_upper in ['A', 'B', 'C']:
                would_take_again += 1
            total_grades += 1
    
    return {
        "popular_tags_hint": popular_tags,
        "top_courses_hint": top_courses,
        "avg_quality_hint": round(mean(q), 2) if q else None,
        "avg_difficulty_hint": round(mean(d), 2) if d else None,
        "review_count_hint": len(reviews),
        "would_take_again_hint": round((would_take_again / total_grades * 100), 1) if total_grades > 0 else None,
    }

def deepseek_min_json(reviews: List[Dict], hints: Dict, api_key: str) -> Dict:
    """Generate AI summary using DeepSeek API."""
    if not api_key: raise RuntimeError("Missing DEEPSEEK_API_KEY")
    MAX_ITEMS, MAX_TEXT = 160, 450
    trimmed = [{**r, "review": (r.get("review") or "")[:MAX_TEXT]} for r in reviews[:MAX_ITEMS]]

    schema = {
        "stats": {
            "aiScore": "string (e.g., '97/100')",
            "reviewCount": "integer",
            "averageQuality": "float",
            "averageDifficulty": "float", 
            "wouldTakeAgain": "string (e.g., '95.4%')"
        },
        "popularTags": [
            {
                "tag": "string",
                "level": "string (good/medium/bad)",
                "mentions": "integer"
            }
        ],
        "recentCourseFeedback": {"<COURSE>": "string paragraph"},
        "extraNote": "string paragraph"
    }
    sys_msg = f"""You are an expert in analyzing professor reviews and summarizing them into a concise and informative summary.

{QUERY_SUMMARY}

Return ONLY valid JSON (no markdown) exactly matching the provided schema and keys."""
    
    user_msg = {
        "schema": schema,
        "hints": hints,
        "reviewsSample": trimmed
    }

    # Debug: Log what we're sending to the API
    logger.info(f"System message: {sys_msg[:200]}...")
    logger.info(f"User message keys: {list(user_msg.keys())}")
    logger.info(f"Schema: {schema}")
    
    r = requests.post(
        f"{DEEPSEEK_BASE}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": DEEPSEEK_MODEL, "messages": [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": json.dumps(user_msg, ensure_ascii=False)},
        ], "stream": False},
        timeout=120,
    )
    r.raise_for_status()
    content = (r.json()["choices"][0]["message"]["content"] or "").strip()
    
    # Debug: Log what the AI returned
    logger.info(f"AI Response: {content[:500]}...")

    # strict parse; tolerate stray prose by slicing braces
    try:
        result = json.loads(content)
        logger.info(f"Parsed JSON keys: {list(result.keys())}")
        return result
    except Exception:
        i, j = content.find("{"), content.rfind("}")
        if i != -1 and j != -1 and j > i:
            result = json.loads(content[i:j+1])
            logger.info(f"Parsed JSON keys (after slicing): {list(result.keys())}")
            return result
        raise