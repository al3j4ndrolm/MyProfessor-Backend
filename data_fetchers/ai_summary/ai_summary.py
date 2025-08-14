#!/usr/bin/env python3
# Minimal: RMP -> DeepSeek -> JSON:
# {
#   "popularTags": [string],
#   "recentCourseFeedback": { "<COURSE>": "<paragraph>" },
#   "strengths": [string],
#   "challenges": [string],
#   "finalTake": string
# }

import argparse, base64, json, os, random, sys, time
from typing import Dict, List, Optional
import requests
from statistics import mean
from supabase import create_client, Client
from dotenv import load_dotenv
from logger import logger

RMP_ENDPOINT = "https://www.ratemyprofessors.com/graphql"
DEEPSEEK_BASE = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

# Load environment variables for Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# Database keys
KEY_PROFESSOR_NAME = "professor_name"
KEY_SCHOOL = "school"
KEY_DEPARTMENT = "department"
KEY_AI_SUMMARY = "ai_summary"

S = requests.Session()
S.headers.update({
    "content-type": "application/json",
    "user-agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/123.0.0.0 Safari/537.36"),
    "origin": "https://www.ratemyprofessors.com",
    "referer": "https://www.ratemyprofessors.com/",
})

def gql(query: str, variables: Optional[Dict] = None) -> Dict:
    time.sleep(random.uniform(0.2, 0.5))
    r = S.post(RMP_ENDPOINT, json={"query": query, "variables": variables or {}}, timeout=30)
    r.raise_for_status()
    j = r.json()
    if j.get("errors"):
        raise RuntimeError(json.dumps(j["errors"]))
    return j["data"]

def b64_node(type_name: str, legacy_id: int) -> str:
    return base64.b64encode(f"{type_name}-{legacy_id}".encode()).decode()

def find_teacher(name: str, school_legacy_id: int) -> Optional[str]:
    q = """
    query($q: TeacherSearchQuery!){
      newSearch{ teachers(query:$q){ edges{ node{ id } } } }
    }"""
    gid = b64_node("School", school_legacy_id)
    d = gql(q, {"q": {"text": name, "schoolID": gid, "fallback": True}})
    edges = d.get("newSearch", {}).get("teachers", {}).get("edges", [])
    return edges[0]["node"]["id"] if edges else None

# Try a few field-name combos to stay short but robust
COURSE_FIELDS = ["courseCode","class","courseName","course","className","courseType"]
ONLINE_FIELDS = ["isForOnlineClass","isOnline","onlineClass"]

def fetch_reviews(teacher_id: str, page_size=25, max_reviews=180) -> List[Dict]:
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
                d = gql(try_query(cfield, ofield), {"id": teacher_id, "first": page_size, "after": after})
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
    if isinstance(v, bool): return v
    if isinstance(v, (int, float)): return bool(v)
    if isinstance(v, str): return v.strip().lower() in ("true","1","yes","y")
    return None

def _norm_course(v) -> Optional[str]:
    if v is None: return None
    s = str(v).strip()
    return None if (not s or s.isdigit()) else s

def _norm_tags(v) -> List[str]:
    if v is None: return []
    if isinstance(v, list): return [str(x).strip() for x in v if str(x).strip()]
    return [p.strip() for p in str(v).split("--") if p.strip()]

def normalize_reviews(rows: List[Dict], course_field: Optional[str], online_field: Optional[str]) -> List[Dict]:
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
    # top tags
    tag_counts: Dict[str, int] = {}
    for r in reviews:
        for t in r.get("tags", []):
            tag_counts[t] = tag_counts.get(t, 0) + 1
    popular_tags = [t for t, _ in sorted(tag_counts.items(), key=lambda kv: -kv[1])[:6]]
    # top courses
    course_counts: Dict[str, int] = {}
    for r in reviews:
        c = r.get("course")
        if c: course_counts[c] = course_counts.get(c, 0) + 1
    top_courses = [c for c, _ in sorted(course_counts.items(), key=lambda kv: -kv[1])[:4]]
    # quick averages (not printed; just grounding)
    q = [r["quality"] for r in reviews if isinstance(r.get("quality"), (int, float))]
    d = [r["difficulty"] for r in reviews if isinstance(r.get("difficulty"), (int, float))]
    return {
        "popular_tags_hint": popular_tags,
        "top_courses_hint": top_courses,
        "avg_quality_hint": round(mean(q), 2) if q else None,
        "avg_difficulty_hint": round(mean(d), 2) if d else None,
    }

def deepseek_min_json(reviews: List[Dict], hints: Dict, api_key: str) -> Dict:
    if not api_key: raise RuntimeError("Missing DEEPSEEK_API_KEY")
    MAX_ITEMS, MAX_TEXT = 160, 450
    trimmed = [{**r, "review": (r.get("review") or "")[:MAX_TEXT]} for r in reviews[:MAX_ITEMS]]

    schema = {
        "popularTags": ["string"],
        "recentCourseFeedback": {"<COURSE>": "string paragraph (2–4 sentences)"},
        "strengths": ["string"],
        "challenges": ["string"],
        "finalTake": "string paragraph"
    }
    sys_msg = "Return ONLY valid JSON (no markdown) exactly matching the provided schema and keys."
    user_msg = {
        "schema": schema,
        "hints": hints,
        "reviewsSample": trimmed,
        "rules": [
            "popularTags: 4–6 items, Title Case, draw primarily from hints.",
            "recentCourseFeedback: use only courses from hints; 2–4 sentences each.",
            "strengths/challenges: 3–5 bullets each, concise and grounded.",
            "finalTake: one short, balanced paragraph.",
            "Output a single JSON object with ONLY these keys."
        ]
    }

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

    # strict parse; tolerate stray prose by slicing braces
    try:
        return json.loads(content)
    except Exception:
        i, j = content.find("{"), content.rfind("}")
        if i != -1 and j != -1 and j > i:
            return json.loads(content[i:j+1])
        raise

def update_professor_summary_by_email(email: str, summary: Dict):
    """
    Update all professor records in Supabase with the AI summary using email as primary identifier.
    """
    if not supabase:
        logger.error("Supabase client not initialized. Cannot update professor summary.")
        return False
    
    try:
        # Find all professor records with this email
        result = supabase.table("professors")\
            .select("*")\
            .eq("email", email)\
            .execute()
        
        if not result.data:
            logger.warning(f"No professor found with email: {email}")
            return False
        
        # Update all records with this email
        supabase.table("professors")\
            .update({KEY_AI_SUMMARY: summary})\
            .eq("email", email)\
            .execute()
        
        logger.info(f"Successfully updated {len(result.data)} professor record(s) with email {email} with AI summary.")
        return True
        
    except Exception as e:
        logger.error(f"Error updating professor with email {email}: {e}")
        return False

def generate_ai_summary(professor_name: str, school: str, professor_email: str, rmp_link: str = None, update_db: bool = True) -> Optional[Dict]:
    """
    Generate AI summary for a professor using their RMP data.
    
    Args:
        professor_name: Name of the professor
        school: School name
        professor_email: Professor's email
        rmp_link: RMP link (optional, will be extracted from RMP if not provided)
        update_db: Whether to update the database with the summary (default: True)
    
    Returns:
        AI summary dict or None if generation fails
    """
    try:
        # Get school RMP code from database
        if not supabase:
            logger.error("Supabase client not initialized. Cannot generate AI summary.")
            return None
        
        # Get school info to find RMP code
        school_result = supabase.table("schools").select("rmp_code").eq("school", school).execute()
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
        api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        if not api_key:
            logger.error("DEEPSEEK_API_KEY not found in environment. Cannot generate AI summary.")
            return None
        
        summary = deepseek_min_json(reviews, hints, api_key)
        
        # Update professor record with AI summary (only if update_db is True)
        if update_db:
            if update_professor_summary_by_email(professor_email, summary):
                logger.info(f"Successfully generated and saved AI summary for {professor_name}")
            else:
                logger.error(f"Failed to save AI summary for {professor_name}")
        else:
            logger.info(f"Successfully generated AI summary for {professor_name} (database update skipped)")
        
        return summary
            
    except Exception as e:
        logger.error(f"Error generating AI summary for {professor_name}: {e}")
        return None

def main():
    ap = argparse.ArgumentParser(description="RMP -> minimal JSON via DeepSeek (plus raw review inspection).")
    ap.add_argument("--name"); ap.add_argument("--school", type=int)
    ap.add_argument("--id")
    ap.add_argument("--email", help="Professor email for database lookup (required for database update)")
    ap.add_argument("--max", type=int, default=180)
    ap.add_argument("--page-size", type=int, default=25)
    ap.add_argument("--out"); ap.add_argument("--pretty", action="store_true")
    ap.add_argument("--print-reviews", dest="print_reviews", action="store_true")
    ap.add_argument("--reviews-out"); ap.add_argument("--ndjson-reviews")
    ap.add_argument("--no-db", action="store_true", help="Skip database update")
    args = ap.parse_args()

    if not args.id and not (args.name and args.school):
        ap.error("Provide --id OR both --name and --school")

    teacher_id = args.id or find_teacher(args.name, args.school)  # type: ignore[arg-type]
    if not teacher_id: print("Professor not found", file=sys.stderr); sys.exit(1)

    reviews = fetch_reviews(teacher_id, args.page_size, args.max)

    # raw review inspection (optional)
    if args.reviews_out:
        with open(args.reviews_out, "w", encoding="utf-8") as f: json.dump(reviews, f, ensure_ascii=False, indent=2)
    if args.ndjson_reviews:
        with open(args.ndjson_reviews, "w", encoding="utf-8") as f:
            for r in reviews: f.write(json.dumps(r, ensure_ascii=False)+"\n")
    if args.print_reviews:
        txt = json.dumps(reviews, ensure_ascii=False, indent=2 if args.pretty else None)
        return sys.stdout.write(txt)

    # DeepSeek -> minimal JSON
    hints = build_hints(reviews)
    out = deepseek_min_json(reviews, hints, api_key=os.environ.get("DEEPSEEK_API_KEY",""))

    # Update the professor record with the AI summary (if email provided)
    if not args.no_db and args.email:
        update_professor_summary_by_email(args.email, out)
    elif not args.no_db:
        logger.warning("Cannot update database. Provide --email for database update.")

    txt = json.dumps(out, ensure_ascii=False, indent=2 if args.pretty else None)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f: f.write(txt)
    else:
        sys.stdout.write(txt)

if __name__ == "__main__":
    main()
