from google import genai
from django.conf import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)


# ─────────────────────────────────────────────
#  ROOM MATCH
# ─────────────────────────────────────────────

def get_vibe_score(user_prefs: str, listing_prefs: str) -> str:
    """
    Score compatibility between a user and a room listing.
    Returns JSON: {"score": int, "reason": str}
    """
    prompt = f"""
You are an expert room-rental compatibility engine for an Indian flatmate platform called StayMatch.
Your job: given a person's preferences and a room listing, return a compatibility score (0–100)
and a specific, honest reason for that score.

━━━━━━━━━━━━━━━━━━
PERSON LOOKING FOR A ROOM:
━━━━━━━━━━━━━━━━━━
{user_prefs}

━━━━━━━━━━━━━━━━━━
ROOM LISTING:
━━━━━━━━━━━━━━━━━━
{listing_prefs}

━━━━━━━━━━━━━━━━━━
CRITICAL SCORING RULE — READ THIS FIRST:
━━━━━━━━━━━━━━━━━━
Your score and your reason MUST be consistent with each other.
- If you mention ANY mismatch or conflict in the reason → score CANNOT be 95 or above.
- If you mention a significant conflict → score MUST reflect that deduction.
- A score of 100 means ZERO conflicts across ALL fields. Only give 100 if reason says "No conflicts found."
- A score of 90+ means only trivial differences. If reason mentions a real mismatch, score must be 89 or lower.
- Do NOT inflate scores to seem helpful. An honest 72 is better than a misleading 100.

━━━━━━━━━━━━━━━━━━
RESULT BEHAVIOUR:
━━━━━━━━━━━━━━━━━━
- Always return a score, even if compatibility is low.
- Never refuse to score. The caller will decide what to show the user.
- Lowest possible score is 5 (hard gender block). Otherwise score between 20–95.

━━━━━━━━━━━━━━━━━━
SCORING RULES — apply in this order:
━━━━━━━━━━━━━━━━━━

GEOGRAPHY (most important):
- Same city → no penalty.
- "Bihar" and "Patna" → compatible (Patna is Bihar's capital). No penalty.
- "NCR" or "Delhi" and "Noida" or "Gurgaon" → compatible. No penalty.
- Different states with no overlap → deduct 40 points. Score cannot exceed 35.
- BLANK city = flexible → no penalty.

BUDGET:
- Rent within person's budget → no penalty.
- Rent exceeds budget by up to 10% → deduct 10 points.
- Rent exceeds budget by 10–25% → deduct 20 points.
- Rent exceeds budget by more than 25% → deduct 35 points. Score cannot exceed 40.
- BLANK budget = flexible → no penalty.

ROOM TYPE:
- Exact match → +10 bonus.
- Compatible types → no penalty.
- Direct conflict (Private vs Shared) → deduct 15 points.
- BLANK = flexible → no penalty.

GENDER PREFERENCE:
- Room says "Female only" but person is Male (or vice versa) → score = 5 maximum.
- "Any" or blank → no penalty.

LIFESTYLE:
- Sleep conflict (Early Riser vs Night Owl) → deduct 12 points.
- Cleanliness conflict (gap of 4+ on 10-point scale) → deduct 10 points.
- Guest policy direct conflict → deduct 8 points.
- BLANK or "Flexible" or "No preference" on EITHER side → zero penalty.

EMPTY / FLEXIBLE FIELDS:
- Person left most fields blank → baseline score 65. Deduct only for genuine conflicts.
- Never penalise for unfilled fields.

BONUS (max +15 total):
- Multiple lifestyle alignments (sleep + cleanliness + guest policy all match) → +10
- Room amenities align with lifestyle → +5

━━━━━━━━━━━━━━━━━━
REASON FORMAT:
━━━━━━━━━━━━━━━━━━
- Exactly 2 sentences. Plain English only. No Hindi. No Hinglish.
- Sentence 1: Strongest reason this IS a good match (use actual values).
- Sentence 2: Biggest concern or mismatch — or "No major conflicts found" if truly clean.
- Your score MUST match what sentence 2 says. If sentence 2 mentions a conflict, score must be lower.
- BAD: "Good match on budget and cleanliness." (too vague)
- GOOD: "The room's ₹12,000 rent fits the user's ₹14,000 budget, and both prefer a clean,
  quiet environment. The only concern is sleep schedule — room prefers early risers but user
  is flexible, which should be discussed before moving in."
"""

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config={
            'temperature': 0.1,
            'response_mime_type': 'application/json',
            'response_schema': {
                "type": "OBJECT",
                "properties": {
                    "score":  {"type": "INTEGER"},
                    "reason": {"type": "STRING"},
                },
                "required": ["score", "reason"],
            }
        }
    )
    return response.text


# ─────────────────────────────────────────────
#  FLATMATE MATCH
# ─────────────────────────────────────────────

def get_flatmate_vibe_score(user_prefs: str, profile_prefs: str) -> str:
    """
    Score compatibility between two people as flatmates.
    Returns JSON: {"score": int, "reason": str}
    """
    prompt = f"""
You are an expert flatmate compatibility engine for an Indian rental platform called StayMatch.
Your job: given Person A's preferences and Person B's profile, score how well they would
work as flatmates (0–100) and give a specific, honest reason.

━━━━━━━━━━━━━━━━━━
PERSON A (searching):
━━━━━━━━━━━━━━━━━━
{user_prefs}

━━━━━━━━━━━━━━━━━━
PERSON B (profile):
━━━━━━━━━━━━━━━━━━
{profile_prefs}

━━━━━━━━━━━━━━━━━━
CRITICAL SCORING RULE — READ THIS FIRST:
━━━━━━━━━━━━━━━━━━
Your score and your reason MUST be consistent with each other.
- If your reason mentions ANY mismatch → score CANNOT be 95 or above.
- If your reason mentions a significant conflict → score MUST reflect that deduction numerically.
- Score of 100 = ZERO conflicts across ALL fields. Only give 100 if reason explicitly says no conflicts.
- Score of 90+ = only trivial differences exist. Any real mismatch → score 89 or lower.
- Do NOT inflate scores to seem helpful. Users will lose trust if score says 100 but reason mentions problems.
- Be honest. A realistic 74 builds more trust than a flattering 100.

━━━━━━━━━━━━━━━━━━
RESULT BEHAVIOUR:
━━━━━━━━━━━━━━━━━━
- Always return a score. Never refuse to score — lowest is 5 (hard gender block).
- Even poor matches get a score. The platform decides what to show — you just score honestly.
- When data has few entries, you may still score — use available fields and note what's missing.

━━━━━━━━━━━━━━━━━━
SCORING RULES — apply in this order:
━━━━━━━━━━━━━━━━━━

GEOGRAPHY:
- Same city → no penalty.
- "Bihar" / "Patna" → same. "Delhi" / "Noida" / "Gurgaon" → same metro. No penalty.
- Different non-overlapping cities → deduct 35 points. Score cannot exceed 40.
- BLANK = flexible → no penalty.

BUDGET:
- Person B's budget within 15% of Person A's → compatible.
- Gap >30% → deduct 15 points.
- BLANK = flexible → no penalty.

GENDER PREFERENCE:
- Person A wants "Male only" but Person B is Female (or vice versa) → score = 5 maximum.
- "Any" or blank → no penalty.

LIFESTYLE DEAL-BREAKERS (binary — conflicts or doesn't):
- Smoking: strict non-smoker vs indoor smoker → deduct 20 points.
- Alcohol: strictly avoids vs drinks regularly → deduct 10 points.
- Pets: has pets vs "No pets" → deduct 15 points.
- Sleep: Early Riser vs Night Owl → deduct 12 points.
- Noise: needs quiet vs lively/social → deduct 10 points.
- Cleanliness: gap of 4+ on 10-point scale → deduct 12 points.
- Guest policy: "No guests" vs "Open House" → deduct 10 points.
- "Flexible", "Any", "No Preference", or BLANK on EITHER side → zero penalty.

LIFESTYLE BONUSES:
- Same occupation type → +8 points.
- Same language preference → +5 points.
- Same sleep schedule → +7 points.
- 3+ lifestyle fields align → +10 points.

EMPTY / FLEXIBLE SEARCHER:
- Person A left most fields blank → baseline 65 for same-city profile. Deduct only real conflicts.

OCCUPATION-BASED AGE INFERENCE:
- Student → roughly 18–23. Working Professional → 23–35. Research/Academia → 24–35.
- Penalise only on wildly mismatched occupation-age combinations.

━━━━━━━━━━━━━━━━━━
REASON FORMAT:
━━━━━━━━━━━━━━━━━━
- Exactly 2 sentences. Plain English only. No Hindi. No Hinglish.
- Sentence 1: Best reason they ARE compatible (use actual field values, not generic phrases).
- Sentence 2: Biggest concern — or "No significant lifestyle conflicts detected" if truly clean.
- CRITICAL: Score must match sentence 2. If sentence 2 mentions a conflict, score must be lower than 95.
- BAD: "They share similar interests." (vague, useless)
- GOOD: "Both are non-smokers who prefer a quiet environment with similar cleanliness levels
  (Person A: relaxed 1-5, Person B: 7/10) — minor gap but manageable.
  The main concern is cleanliness expectations differ by about 2-3 points, which should be
  discussed before committing."
"""

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config={
            'temperature': 0.1,
            'response_mime_type': 'application/json',
            'response_schema': {
                "type": "OBJECT",
                "properties": {
                    "score":  {"type": "INTEGER"},
                    "reason": {"type": "STRING"},
                },
                "required": ["score", "reason"],
            }
        }
    )
    return response.text


