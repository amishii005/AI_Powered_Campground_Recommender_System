🏕️ AI-Powered Natural Language Campground Recommender & Booking System

A smart, full-stack web application that allows users to search for campgrounds using natural language queries, get AI-powered recommendations, check availability, add to cart, and book — all with a friendly, interactive UI.

🛠 Tech Stack

Frontend: HTML, CSS, JavaScript (Flask Templates)
Backend: Python (Flask) + spaCy (NLP)
Database: JSON-based storage (campgrounds, users, bookings)
AI/NLP: spaCy for natural language preference extraction
HTTP Client: Axios (optional for async calls)

🚀 Live Demo

🔗 Click here to view live (http://127.0.0.1:5000/login)

📸 Preview

(Add screenshots of Home Page, Search Results, Cart, Checkout, Owner Dashboard)

📁 Folder Structure
AI_NATURAL_LANGUAGE_RECOMMENDER_SYSTEM/
│── static/                 # CSS, JS, images
│── templates/              # HTML templates
│   ├── home.html
│   ├── login.html
│   ├── owner_dashboard.html
│   ├── cart.html
│   ├── checkout_success.html
│── app.py                   # Flask main app
│── recommender.py           # AI recommendation logic
│── users.json               # User data
│── campgrounds.json         # Campground listings
│── bookings.json            # Booking records
│── logs/                    # Daily interaction logs
│── requirements.txt
│── README.md

⚙️ Features

✅ Natural Language Search – e.g., "Need a tent in Himachal with bonfire and toilets from Jan 20 to Jan 22"
✅ AI-Powered Recommendations – Extracts location, type, activities, amenities from query
✅ Availability Checking – Filters out already booked dates
✅ Match Score Display – Shows how well each result matches user preferences
✅ Add to Cart & Checkout – Session-based cart with booking confirmation
✅ Owner Dashboard – Add, edit, and manage campground listings
✅ Daily Interaction Logging – Stores user queries and results in logs

🚀 Getting Started
🔙 Backend Setup
# Clone repo
git clone https://github.com/amishii005/AI_Powered_Campground_Recommender_System.git

# Go to project folder
cd AI_Powered_Campground_Recommender_System

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Run Flask server
python app.py


Backend running on: http://127.0.0.1:5000

🔌 API Endpoints

Base URL: http://127.0.0.1:5000

Method	Endpoint	Description
POST	/search	Get campground recommendations based on query
POST	/add_to_cart	Add selected campground to cart
POST	/checkout	Finalize booking
GET	/favorites	View saved campgrounds
📦 Dependencies

Backend:

Flask
Flask-Session
spaCy

🧩 Main Components
Component	Purpose
extract_preferences()	Extracts structured preferences from user query
match_campgrounds()	Scores and filters campgrounds based on preferences
Cart System	Stores user’s selected campgrounds in session
Availability Checker	Prevents booking overlaps
Owner Dashboard	Manage listings
👤 Author

Amishi Gupta
📌 LinkedIn
📌 GitHub
