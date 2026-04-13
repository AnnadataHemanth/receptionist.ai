🤖 AI Voice-Based Appointment Booking System (Jarvis)

📌 Overview

This project is an AI-powered voice assistant that automates appointment booking through phone calls. Users interact using natural speech, and the system processes the request, extracts details, and schedules appointments.

---

🚀 Features

- 📞 Voice-based appointment booking
- 🧠 AI-powered intent and entity extraction
- 📩 SMS confirmation system
- 🗂️ Admin dashboard
- 🔍 Search and sorting
- 🔐 Secure authentication
- ⚡ Fallback logic

---

🛠️ Tech Stack

- FastAPI
- Groq API (LLM)
- Twilio (Voice + SMS)
- SQLite
- HTML, CSS
- ngrok

---

⚙️ Setup Instructions

1️⃣ Clone the Repository

git clone https://github.com/your-username/receptionist.ai.git
cd receptionist.ai

---

2️⃣ Create Virtual Environment

python -m venv venv
venv\Scripts\activate

---

3️⃣ Install Dependencies

pip install -r requirements.txt

---

4️⃣ Configure Environment Variables

Create ".env" file:

TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=your_twilio_number
GROQ_API_KEY=your_groq_key
SECRET_KEY=your_secret

---

5️⃣ Run the Server

uvicorn app.main:app --reload

---

🌐 Running the Project

Option 1: Local Testing (No Twilio)

Access:

http://127.0.0.1:8000/admin/bookings

---

Option 2: Full System (Voice + SMS)

---

📞 Twilio Setup (Step-by-Step)

1️⃣ Create Twilio Account

Go to: https://www.twilio.com
Sign up and verify your phone number.

---

2️⃣ Get Credentials

From Twilio Console:

- Account SID
- Auth Token
- Twilio Phone Number

Add them to ".env".

---

3️⃣ Buy / Use Twilio Number

- Go to Phone Numbers → Manage → Buy a Number
- Choose a number with Voice capability

---

4️⃣ Start ngrok

ngrok http 8000

Copy the HTTPS URL.

---

5️⃣ Configure Webhook in Twilio

Go to:

- Phone Numbers → Your Number

Under Voice Configuration:

Set:

Webhook URL → https://your-ngrok-url/voice
Method → POST

---

6️⃣ Test the System

- Call your Twilio number
- Speak naturally (e.g., “Book appointment tomorrow at 4 PM”)
- System will:
  - Understand input
  - Store booking
  - Send SMS confirmation

---

📊 Admin Dashboard

http://127.0.0.1:8000/admin/login

Use: 
Username: admin
Password: 1234

http://127.0.0.1:8000/admin/bookings

To see the dashboard and bookings.

---

🧠 How It Works

1. User calls Twilio number
2. Speech → text
3. AI processes input
4. Extracts details
5. Saves to database
6. Sends SMS
7. Displays in dashboard

---

🔐 Security

- Environment variables used for API keys
- ".env" excluded via ".gitignore"

---

⚠️ Important Notes

- ngrok is required for Twilio integration
- Localhost alone cannot receive Twilio requests
- ngrok is only for development

---

🔮 Future Enhancements

- Multilingual support
- Better voice output
- Cloud deployment
- Calendar integration

---

👨‍💻 Author

Annadata Hemanth
B.Tech AI & Data Science

---

📜 License

This project is licensed under the MIT License.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files, to deal in the software
without restriction, including without limitation the rights to use, copy,
modify, merge, publish, distribute, sublicense, and/or sell copies of the software.

See the LICENSE file for more details.