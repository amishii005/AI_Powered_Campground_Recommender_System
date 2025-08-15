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

<img width="1793" height="739" alt="image" src="https://github.com/user-attachments/assets/916b62a6-8297-4c38-a478-21c1b9edb80a" />
<img width="1884" height="878" alt="image" src="https://github.com/user-attachments/assets/5aaa19b7-5f9a-49c9-b792-4737d861f339" />
<img width="1873" height="693" alt="image" src="https://github.com/user-attachments/assets/fc0428f7-5d92-4a8b-ba9f-7e53812db0e8" />
<img width="1876" height="602" alt="image" src="https://github.com/user-attachments/assets/000d1bad-36ba-4875-baa3-555181f7d637" />


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
