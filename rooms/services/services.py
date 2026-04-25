from google import genai
from django.conf import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def get_vibe_score(user_prefs, room_prefs):
    prompt = f"""
    User preferences: {user_prefs}
    Room preferences: {room_prefs}
    Compare these and give a compatibility score from 0-100.
    Return ONLY this JSON, nothing else, no markdown, no extra text:
    {{"score": 85, "reason": "brief reason here"}}
    """
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    return response.candidates[0].content.parts[0].text