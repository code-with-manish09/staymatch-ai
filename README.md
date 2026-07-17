# staymatch-ai# 🏠 StayMatch — Find a Flatmate Who Actually Gets You

**StayMatch** is an AI-powered room rental and flatmate matching platform built for students and young professionals across India. Instead of matching people on budget alone, StayMatch scores real compatibility — sleep schedule, lifestyle, hobbies, and personality — using **Google's Gemini AI**, so you find a flatmate (or a room) that actually fits how you live.

🔗 **Live Demo:** [codewithrudra0976codewithrudra.pythonanywhere.com](https://codewithrudra0976codewithrudra.pythonanywhere.com)
📦 **Repository:** [github.com/code-with-manish09/staymatch-ai](https://github.com/code-with-manish09/staymatch-ai)

---



## ✨ What StayMatch Does

StayMatch solves two problems in one platform:

1. **Room Rental** — Got a spare room? List it. Looking for one? Browse and inquire, all in one place.
2. **AI Flatmate Matching** — Whether you already have a room and need a flatmate, or you're looking for a room *and* a flatmate to share it with, StayMatch's "Post Flatmate" flow captures which scenario applies to you, so listings never get confusing.

At the core is a **Match Gateway** — a single AI-matching engine that works for both rooms and flatmates. Users fill in a short preference form, and Gemini AI cross-references it against the full listing/profile database using a strict evaluation prompt — returning the best-fit cards along with a **compatibility percentage and a written explanation of *why* it's a good match.**

---

## 🚀 Key Features

### 🤖 AI-Powered Matching
- Gemini AI scores compatibility across multiple lifestyle dimensions — sleep schedule, cleanliness, food habits, noise tolerance, budget, and social style.
- Every match comes with a **percentage score + a plain-language explanation** of why you matched.
- One unified matching engine (`Match Gateway`) handles both **room seekers** and **flatmate seekers**.

### 🧠 Personality Quiz
- A quick 8-step quiz (sleep cycle, food preference, hobbies, sports, occupation, and more).
- AI converts answers into personality **tags** (e.g. *Night Owl, Gamer, The Planner*) that appear on the user's dashboard profile.
- Purely for engagement and profile richness — not tied to the matching algorithm.

### 🔐 Secure Authentication
- Google OAuth login via `django-allauth` — no manual signup friction.
- JWT-based REST authentication (`djangorestframework-simplejwt`) for API-level auth.

### 🏠 Dual Listings — Rooms & Flatmates
- **Post a Room** — list an available room for rent with AI-suggested pricing based on similar nearby listings.
- **Post a Flatmate Profile** — clearly marked as *"I have a room, need a flatmate"* or *"I need a room, looking to share"* to avoid confusion on the details page.

### 💬 In-App Messaging & Auto-Inquiry
- Hit **Inquire** on any room or flatmate card and an auto-generated message is sent to the poster to kick off the conversation.
- Dedicated inbox/chat view for every ongoing conversation — no need to exchange personal numbers upfront.

### 📊 Personalized Dashboard
- **Discover** — Browse room and flatmate cards (5 visible per section with horizontal scroll, "View All" to see the rest).
- **My Activity** — Track your own posted rooms and flatmate listings separately, with views, leads, and status (Live/Draft).
- **Saved** — Bookmark rooms and flatmate profiles you're interested in, organized in separate tabs.
- **Live Platform Stats** — Total users joined, total listings, and a city-wise breakdown of active rooms & flatmates.
- **Reviews Carousel** — Recent reviews from users, pulled from room details, surfaced on the dashboard for social proof.

### 🗺️ Additional Highlights
- Gender preference filters for safer matching.
- City, budget, room type, and furnishing filters on the discover feed.
- Profile completion tracker with a visual progress ring.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Django (Python) |
| **Frontend** | HTML, CSS, JavaScript (Django Templates) |
| **AI / Matching** | Google Gemini API |
| **Authentication** | Google OAuth (`django-allauth`) + JWT (`djangorestframework-simplejwt`) |
| **Database** | SQLite |
| **Deployment** | PythonAnywhere |

---

## ⚙️ Local Setup

```bash
# Clone the repository
git clone https://github.com/code-with-manish09/staymatch-ai.git
cd staymatch-ai

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (see below)
# create a .env file in the project root

# Run migrations
python manage.py migrate

# Start the development server
python manage.py runserver
```

### 🔑 Environment Variables

Create a `.env` file in the project root with:

```
SECRET_KEY=your-django-secret-key
GEMINI_API_KEY=your-gemini-api-key
GOOGLE_OAUTH_CLIENT_ID=your-google-oauth-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-oauth-client-secret
```

You'll also need to configure your OAuth redirect URI in [Google Cloud Console](https://console.cloud.google.com) under **APIs & Services → Credentials**:
```
http://localhost:8000/accounts/google/login/callback/
```

---

## 📁 Project Structure

```
staymatch-ai/
├── accounts/       # User auth, profile management, Google OAuth
├── core/           # Project settings, root URLs
├── dashboard/      # Dashboard views (discover, activity, saved, quiz)
├── home/           # Landing page
├── inbox/          # Messaging & auto-inquiry system
├── rooms/          # Room listings, flatmate profiles, AI matching (services.py)
├── static/         # CSS, JS, images
├── media/          # User-uploaded photos
├── templates/      # HTML templates per app
└── manage.py
```

---

## 🚧 Future Improvements

- Persistent database (PostgreSQL) for production scale
- In-app notifications with real-time updates
- Map-based listing discovery (currently mocked on landing page)
- Payment integration for premium listings

---

## 📬 Contact

- **Email:** mynameisrudraa@gmail.com
- **LinkedIn:** [linkedin.com/in/manish-kumar-4378a03a2](https://www.linkedin.com/in/manish-kumar-4378a03a2)

---

*Built solo, end-to-end — from database design to AI prompt engineering to deployment.*
