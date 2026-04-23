from groq import Groq
import json
from app.core.config import GROQ_API_KEY

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)


def extract_booking_details(user_speech: str):
    try:
        prompt = f"""
        Extract the following details from the user input:

        - intent (book / cancel / unknown)
        - date
        - time
        - name
        Rules: 
        - Name should be a proper human name (not phrases like "hey month" or "next week" )
        - If unsure, return closest valid name
        - Prefer common Indian names if phonetic match exists
        - Do not include phrases like "my name is" , "this is" , "i am" in the name field
        Respond ONLY in JSON format like:
        {{
            "intent": "...",
            "date": "...",
            "time": "...",
            "name": "..."
        }}

        User input: "{user_speech}"
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # stable free model
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        raw_output = response.choices[0].message.content.strip()
        print("RAW AI:", raw_output)

        # Clean JSON (remove ```json if present)
        if raw_output.startswith("```"):
            raw_output = raw_output.split("```")[1]
            raw_output = raw_output.replace("json", "").strip()

        data = json.loads(raw_output)
        return data

    except Exception as e:
        print("AI ERROR:", e)
        return {
            "intent": "unknown",
            "date": None,
            "time": None,
            "name": None
        }