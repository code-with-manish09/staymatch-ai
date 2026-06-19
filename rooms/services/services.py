from google import genai
from django.conf import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def get_vibe_score(user_prefs, room_prefs):
    prompt = f"""
You are a room/flatmate compatibility scoring AI.

User preferences: {user_prefs}
Room/Profile preferences: {room_prefs}

Compare carefully and give a compatibility score from 0 to 100.
- City mismatch = low score
- Budget mismatch = low score  
- Sleep schedule mismatch = lower score
- Only give high score when genuinely highly compatible

IMPORTANT: Write the reason in English only. No Hindi, no Hinglish.

Return ONLY this JSON, no backticks, no extra text:
{{"score": 72, "reason": "write reason here in English"}}
"""
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    return response.candidates[0].content.parts[0].text

    #========faqs==========

def get_room_faqs(room_details, user_question):
    prompt = f"""
you are a helpful assistant for a room rental platform.
 room details: {room_details}
user question: { user_question}

Answer based on room details. For obvious facts like country (India), currency (INR/Rupees), 
use your general knowledge. Be helpful, friendly and concise.
If truly not available, say "This information is not available for this room."
Return only the answer, no extra text.
"""
    response = client.models.generate_content(
        model = 'gemini-2.5-flash',
        contents = prompt
    )

    return response.candidates[0].content.parts[0].text
