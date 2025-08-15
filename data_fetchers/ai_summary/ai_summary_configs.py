import os

RMP_ENDPOINT = "https://www.ratemyprofessors.com/graphql"
DEEPSEEK_BASE = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

HEADER = {
    "content-type": "application/json",
    "user-agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/123.0.0.0 Safari/537.36"),
    "origin": "https://www.ratemyprofessors.com",
    "referer": "https://www.ratemyprofessors.com/",
}

QUERY_SUMMARY = """
You are an expert in analyzing professor reviews and summarizing them into a concise and informative summary.

You will receive a dataset of professor reviews in JSON format from RateMyProfessors or similar sources.

Your task is to analyze the dataset and produce a structured JSON summary with the following sections:


You will receive a dataset of professor reviews in JSON format from RateMyProfessors or similar sources.  
Analyze the dataset and produce a structured JSON summary with the following sections:  

1. **Stats**  
   - Calculate the average values for:  
     - Average Quality  
     - Average Difficulty  
     - Would Take Again %  
   - Generate an **AI Recommend Score** (0–100) based on all given reviews (you decide the formula but ensure consistency).  
   - Also include a `reviewCount` with the total number of reviews.

2. **Popular Tags**  
   - Extract the most frequently mentioned tags from the reviews.  
   - Count how many times each tag appears.  
   - Assign each tag a `level`:  
     - `"good"` = positive sentiment tags  
     - `"medium"` = neutral/mixed sentiment tags  
     - `"bad"` = negative sentiment tags  
   - Return as an array of objects with fields:  
     - `tag` (string)  
     - `level` (string: good/medium/bad)  
     - `mentions` (integer)  

3. **Recent Course Feedback**  
   - Group reviews by course code.  
   - Summarize the common feedback for each course in one concise sentence.  
   - If multiple course codes have highly similar feedback, merge them into one combined entry with a comma-separated list of course codes as the key.  
   - Keep the summaries focused on feedback patterns (e.g., workload, grading, lecture quality).

4. **Extra Note**  
   - Highlight any trend, interesting insight, or uncommon observation **not already covered** in Stats, Tags, or Course Feedback.
---

Return your response strictly in the following JSON structure (do not add explanations or text outside the JSON):

{
  "stats": {
    "aiScore": "97/100",
    "reviewCount": 56,
    "averageQuality": 4.18,
    "averageDifficulty": 2.95,
    "wouldTakeAgain": "95.4%"
  },
  "extraNote": "There is a noticed trend in the recent reviews that heavy homework is mentioned more frequently.",
  "popularTags": [
    {"tag": "Caring", "level": "good", "mentions": 22},
    {"tag": "Amazing lectures", "level": "good", "mentions": 21},
    ...
  ],
  "recentCourseFeedback": {
    "MATH1A": "The course includes lots of homework but is balanced by fair quizzes and tests. Many find his teaching style effective for mastering calculus.",
    "MATH1B": "Students appreciate his extra credit opportunities and fair grading. Many find the workload manageable with consistent effort.",
    "MATH1C, MATH1D": "Some students note the course is challenging but appreciate his extra credit and clear expectations. His teaching style makes complex topics more approachable.",
    "MATH10, MATH31, MATH32": "The course is noted for its manageable workload and open-book exams. Group projects and extra credit opportunities are frequently mentioned as positives."
  }
}
"""