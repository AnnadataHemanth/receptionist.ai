import re
from pydantic import BaseModel
from fastapi import APIRouter, Request
from fastapi.responses import Response
from datetime import datetime, timedelta
from database import get_all_bookings
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi import Form
from ai import extract_booking_details




import random

greetings = [
    "Hello! I’m Jarvis. Hemanth's A I Assistant, How can I assist you today?",
    "Hi there! This is Jarvis. Hemanth's A I Assistant, What can I help you with?",
    "Good day! You have reached Jarvis. Hemanth's A I Assistant, How may I help?"
]

ask_date_variations = [
    "Sure, what date would you like to book?",
    "Absolutely. Which date works for you?",
    "Great. What day should I schedule it for?"
]

ask_time_variations = [
    "Perfect. What time works best for you?",
    "Got it. What time should I lock in?",
    "Alright. What time would you prefer?"
]


NGROK_BASE_URL = "https://simonne-nonsensate-semisuccessfully.ngrok-free.dev"

conversation_state = {}

class TestCallData(BaseModel):
    from_number: str
    message: str

router = APIRouter()

@router.get("/health")
def health_check():
    return {"health": "ok"}

@router.get("/hello")
def hello():
    return {
        "message": "Hello, I am Jarvis. Your server is working."
    }

@router.post("/test-call")
async def test_call(data: TestCallData):

    print("Incoming webhook data:", data)

    caller = data.from_number
    message = data.message.lower()

    try:
        ai_data = extract_booking_details(message)
        intent = ai_data.get("intent")
        ai_date = ai_data.get("date")
        ai_time = ai_data.get("time")
        ai_name = ai_data.get("name")
    except Exception:
        intent = "unknown"
        ai_date = None
        ai_time = None
        ai_name = None

    if caller not in conversation_state:
        if intent == "book" and ai_date and ai_time and ai_name:
            from database import save_booking
            save_booking(ai_name, caller, ai_date, ai_time)

            try:
                from sms import send_sms
                send_sms(caller, f"Hi {ai_name}, your appointment is confirmed for {ai_date} at {ai_time}.")
            except:
                pass

            reply = f"""
        <speak>
        <prosody rate="85%">
            Perfect {ai_name}. Your appointment is confirmed for {ai_date} at {ai_time}.
        </prosody>
    </speak>
    """

            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">
        {reply}
    </Say>
    <Hangup/>
</Response>
"""
            return Response(content=twiml, media_type="application/xml")
        
        if "appointment" in message:
            conversation_state[caller] = "waiting_for_date"
            reply = "Sure. For which date would you like to book the appointment?"
        else:
            reply = "I have received your message."

        return {
            "jarvis_reply": reply,
            "state": conversation_state.get(caller)
        }

from fastapi.responses import PlainTextResponse

from fastapi import Request
from fastapi.responses import Response
from fastapi import Request
from fastapi.responses import Response

@router.post("/voice")
async def voice_webhook(request: Request):
    base_url = str(request.base_url).rstrip("/")

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech"
            action="{base_url}/process_speech"
            method="POST"
            timeout="5">
        <Say voice="alice">
            {random.choice(greetings)}
        </Say>

    </Gather>
</Response>
"""
    return Response(content=twiml, media_type="application/xml")

@router.post("/process_speech")
async def process_speech(request: Request):
    form = await request.form()

    user_speech = form.get("SpeechResult", "").lower()
    caller = form.get("From") or "unknown"
    try:
        ai_data = extract_booking_details(user_speech)
        print("AI DATA:", ai_data)
        intent = ai_data.get("intent")
        ai_date = ai_data.get("date")
        ai_time = ai_data.get("time")
        ai_name = ai_data.get("name")
    except Exception:
        intent = "unknown"
        ai_date = None
        ai_time = None
        ai_name = None

    # fallback if AI fails
    if intent == "unknown":
        if "book" in user_speech or "appointment" in user_speech:
            intent = "book"

    if not ai_date:
        if "today" in user_speech:
            ai_date = "today"
        elif "tomorrow" in user_speech:
            ai_date = "tomorrow"

    if not ai_time:
        match = re.search(r'\d{1,2}(:\d{2})?\s?(am|pm)', user_speech)
        if match:
            ai_time = match.group()

    if not ai_name:
        if "my name is" in user_speech:
            ai_name = user_speech.split("my name is")[-1].strip().split()[0].title()

    base_url = str(request.base_url).rstrip("/")

    # ---- GLOBAL CANCEL ----
    if any(word in user_speech for word in ["cancel", "stop", "never mind"]):
        if caller in conversation_state:
            del conversation_state[caller]

            twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">
        No problem. I have cancelled the request.
    </Say>
    <Hangup/>
</Response>
"""
        return Response(content=twiml, media_type="application/xml")

    booking_keywords = ["appointment", "book", "schedule", "meeting", "visit"]

    # ---- NOT IN FLOW YET ----
    if caller not in conversation_state:

        if intent == "book":

            today = datetime.now()

            # Detect date
            if "today" in user_speech:
                parsed_date = today.strftime("%Y-%m-%d")
            elif "tomorrow" in user_speech:
                parsed_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
            else:
                parsed_date = None

            # Normalize speech
            normalized_speech = user_speech.replace(".", "").replace("p m", "pm").replace("a m", "am")

            time_match = re.search(r'\b\d{1,2}(:\d{2})?\s?(am|pm)\b', normalized_speech)

            # If both date and time detected → skip steps and ask name
            if parsed_date and time_match:
                parsed_time = time_match.group()

                conversation_state[caller] = {
                    "step": "waiting_for_name",
                    "date": parsed_date,
                    "time": parsed_time
                }

                twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech"
            action="{base_url}/process_speech"
            method="POST"
            timeout="5">
        <Say voice="alice">
            May I have your name for the booking?
        </Say>
    </Gather>
</Response>
"""
                return Response(content=twiml, media_type="application/xml")

            # Otherwise ask for date
            conversation_state[caller] = {"step": "waiting_for_date"}

            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech"
            action="{base_url}/process_speech"
            method="POST"
            timeout="5">
        <Say voice="alice">
            Sure. What date would you like to book?
        </Say>
    </Gather>
</Response>
"""
            return Response(content=twiml, media_type="application/xml")

        else:
            reply = f"You said: {user_speech}"

            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">
        {reply}
    </Say>
    <Hangup/>
</Response>
"""
            return Response(content=twiml, media_type="application/xml")

    # ---- WAITING FOR DATE ----
    elif conversation_state[caller]["step"] == "waiting_for_date":

        if len(user_speech) < 2:
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech"
            action="{base_url}/process_speech"
            method="POST"
            timeout="5">
        <Say voice="alice">
            I didn’t quite catch the date. Could you repeat it?
        </Say>
    </Gather>
</Response>
"""
            return Response(content=twiml, media_type="application/xml")

        today = datetime.now()

        if "today" in user_speech:
            parsed_date = today.strftime("%Y-%m-%d")
        elif "tomorrow" in user_speech:
            parsed_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            parsed_date = user_speech

        conversation_state[caller]["date"] = parsed_date
        conversation_state[caller]["step"] = "waiting_for_time"

        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech"
            action="{base_url}/process_speech"
            method="POST"
            timeout="5">
        <Say voice="alice">
            Great. What time works best for you?
        </Say>
    </Gather>
</Response>
"""
        return Response(content=twiml, media_type="application/xml")

    # ---- WAITING FOR TIME ----
    elif conversation_state[caller]["step"] == "waiting_for_time":

        if len(user_speech) < 2:
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech"
            action="{base_url}/process_speech"
            method="POST"
            timeout="5">
        <Say voice="alice">
            I didn’t hear the time clearly. Could you say it again?
        </Say>
    </Gather>
</Response>
"""
            return Response(content=twiml, media_type="application/xml")

        conversation_state[caller]["time"] = user_speech
        conversation_state[caller]["step"] = "waiting_for_name"

        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech"
            action="{base_url}/process_speech"
            method="POST"
            timeout="5">
        <Say voice="alice">
            May I have your name for the booking?
        </Say>
    </Gather>
</Response>
"""
        return Response(content=twiml, media_type="application/xml")

    # ---- WAITING FOR NAME ----
    elif conversation_state[caller]["step"] == "waiting_for_name":

        if len(user_speech) < 2:
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech"
            action="{base_url}/process_speech"
            method="POST"
            timeout="5">
        <Say voice="alice">
            I didn’t catch your name. Could you repeat it please?
        </Say>
    </Gather>
</Response>
"""
            return Response(content=twiml, media_type="application/xml")

        name = user_speech.title()
        date = conversation_state[caller]["date"]
        time = conversation_state[caller]["time"]

        reply = f"Thank you {name}. Your appointment is confirmed for {date} at {time}. We look forward to seeing you."
        from sms import send_sms
        sms_message = f"Hi {name}, your appointment is confirmed for {date} at {time}."
        try:
            from sms import send_sms
            sms_message = f"Hi {name}, your appointment is confirmed for {date} at {time}."
            send_sms(caller, sms_message)
        except Exception as e:
            print("SMS ERROR:", e)


        from database import save_booking
        save_booking(name, caller, date, time)


        del conversation_state[caller]

        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">
        {reply}
    </Say>
    <Hangup/>
</Response>
"""
        return Response(content=twiml, media_type="application/xml")
    
@router.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page():
    return """
    <html>
    <body style="font-family: Arial; background:#f4f6f9; display:flex; justify-content:center; align-items:center; height:100vh;">
        <form method="post" action="/admin/login"
              style="background:white; padding:30px; border-radius:10px; box-shadow:0 4px 10px rgba(0,0,0,0.1);">
            <h2>Admin Login</h2>
            <input type="text" name="username" placeholder="Username"
                   style="display:block; margin-bottom:10px; padding:8px; width:200px;">
            <input type="password" name="password" placeholder="Password"
                   style="display:block; margin-bottom:10px; padding:8px; width:200px;">
            <button type="submit"
                    style="padding:8px 12px; background:#3498db; color:white; border:none; border-radius:5px;">
                Login
            </button>
        </form>
    </body>
    </html>
    """
@router.post("/admin/login")
async def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "1234":
        request.session["admin"] = True
        return RedirectResponse(url="/admin/bookings", status_code=303)
    else:
        return RedirectResponse(url="/admin/login", status_code=303)

@router.get("/admin/logout")
async def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/admin/login", status_code=303)

@router.get("/admin/bookings", response_class=HTMLResponse)
async def view_bookings(request: Request):
    if not request.session.get("admin"):
        return RedirectResponse(url="/admin/login", status_code=303)
    from database import get_all_bookings
    query = request.query_params.get("q")
    sort = request.query_params.get("sort")

    if query:
        from database import search_bookings
        bookings = search_bookings(query)
    elif sort == "time":
        from database import get_sorted_by_time_of_day
        bookings = get_sorted_by_time_of_day()
    else:
        bookings = get_all_bookings()

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Dashboard - Appointments</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f6f9;
                margin: 0;
                padding: 0;
            }}
            .container {{
                width: 90%;
                margin: 40px auto;
            }}
            h1 {{
                text-align: center;
                color: #333;
            }}
            .card {{
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th {{
                background-color: #2c3e50;
                color: white;
                padding: 12px;
                text-align: left;
            }}
            td {{
                padding: 12px;
                border-bottom: 1px solid #ddd;
            }}
            tr:hover {{
                background-color: #f1f1f1;
            }}
            .summary {{
                margin-bottom: 20px;
                font-size: 18px;
                color: #555;
            }}
        </style>
    </head>
    <body>
    <nav style="
    background:#2c3e50;
    padding:12px 20px;
    display:flex;
    justify-content:space-between;
    align-items:center;
    color:white;
">
    <div style="font-size:18px; font-weight:bold;">
        Jarvis Admin
    </div>

    <div>
        <a href="/admin/bookings" style="color:white; margin-right:15px; text-decoration:none;">Dashboard</a>
        <a href="/admin/add-demo" style="color:white; margin-right:15px; text-decoration:none;">Add Demo</a>
        <a href="/admin/bookings?sort=time" style="color:white; margin-right:15px; text-decoration:none;">Sort</a>
        <a href="/admin/logout" style="color:#e74c3c; text-decoration:none;">Logout</a>
    </div>
</nav>
        <div class="container" style="margin-top:20px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h1>Admin Dashboard</h1>
                <a href="/admin/logout"
                    style="padding:8px 12px; background:#e74c3c; 
                    color:white; border-radius:5px; 
                    text-decoration:none;">
                    Logout
                </a>
            </div>
            <form method="get" action="/admin/bookings" style="margin-bottom: 20px;">
                <input type="text" name="q" placeholder="Search by name, phone or date"
                    style="padding: 8px; width: 250px; border-radius: 5px; border: 1px solid #ccc;">
                <button type="submit"
                    style="padding: 8px 12px; border: none; background: #3498db; color: white; border-radius: 5px;">
                    Search
                </button>

            <a href="/admin/bookings?sort=time"
                style="margin-left: 10px; padding: 8px 12px; 
                background: #2ecc71; color: white; 
                border-radius: 5px; text-decoration: none;">
                Sort by Time of Day
            </a>

            <a href="/admin/bookings"
                style="margin-left: 10px; text-decoration: none; color: #555;">
                Reset
            </a>
            </form>
        <div class="card">
                <div class="summary">
                    Total Appointments: <strong>{len(bookings)}</strong>
                </div>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Phone</th>
                        <th>Date</th>
                        <th>Time</th>
                        <th>Action</th>
                    </tr>
    """

    for b in bookings:
        html += f"""
                    <tr>
                        <td>{b[0]}</td>
                        <td>{b[1]}</td>
                        <td>{b[2]}</td>
                        <td>{b[3]}</td>
                        <td>{b[4]}</td>
                        <td>
                            <a href="/admin/delete/{b[0]}" 
                            style="color: white; 
                            background: #e74c3c; 
                            padding: 6px 10px; 
                            border-radius: 5px; 
                            text-decoration: none;">
                            Delete
                            </a>
                        </td>
                    </tr>
        """

    html += """
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    return html


from fastapi.responses import RedirectResponse
from database import delete_booking

@router.get("/admin/delete/{booking_id}")
async def delete_booking_route(booking_id: int):
    delete_booking(booking_id)
    return RedirectResponse(url="/admin/bookings", status_code=303)

@router.get("/admin/add-demo")
async def insert_demo():
    from database import add_demo_data
    add_demo_data()
    return {"status": "Demo data inserted"}