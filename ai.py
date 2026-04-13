import os
from groq import Groq
import json
import re
from dotenv import load_dotenv
load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

def extract_booking_details(text):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "Extract booking info. Return ONLY JSON."
                },
                {
                    "role": "user",
                    "content": f"""
                    Extract booking details from:
                    "{text}"

                    Return JSON:
                    {{
                        "intent": "book/cancel/unknown",
                        "date": "",
                        "time": "",
                        "name": ""
                    }}
                    """
                }
            ],
            temperature=0
        )

        result = response.choices[0].message.content.strip()

# 🔥 remove markdown and extra text
        if "```" in result:
            result = result.split("```")[1]  # get inside block

        if result.startswith("json"):
            result = result.replace("json", "", 1).strip()

# remove anything after closing }
        if "}" in result:
            result = result[:result.rfind("}")+1]
        print("RAW AI:", result)

        data = json.loads(result)

    except Exception as e:
        print("AI ERROR:", e)
        data = {}

    # 🔥 FALLBACK LOGIC (VERY IMPORTANT)
    text_lower = text.lower()

    # intent fallback
    if not data.get("intent") or data.get("intent") == "unknown":
        if any(word in text_lower for word in ["book", "appointment", "schedule"]):
            data["intent"] = "book"

    # date fallback
    if not data.get("date"):
        if "today" in text_lower:
            data["date"] = "today"
        elif "tomorrow" in text_lower:
            data["date"] = "tomorrow"

    # time fallback
    if not data.get("time"):
        match = re.search(r'\d{1,2}(:\d{2})?\s?(am|pm)', text_lower)
        if match:
            data["time"] = match.group()

    # name fallback (basic)
    if not data.get("name"):
        if "my name is" in text_lower:
            name = text_lower.split("my name is")[-1].strip().split()[0]
            data["name"] = name.title()

    intent = data.get("intent", "").lower()
    
    if intent not in ["book", "cancel"]:
        intent = "unknown"

    date = data.get("date") or None
    time = data.get("time") or None
    name = data.get("name") or None

    return {
        "intent": intent,
        "date": date,
        "time": time,
        "name": name
        }