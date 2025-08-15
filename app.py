from flask import Flask, render_template, request, session, redirect, url_for, jsonify  # type: ignore
from flask_session import Session  # type: ignore
import json
from datetime import datetime
import os
from recommender import extract_preferences, match_campgrounds, is_available

CAMPGROUND_DATA_PATH = "campground.json"
USER_DATA_PATH = "users.json"
BOOKINGS_DATA_PATH = "bookings.json"

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Load campgrounds
with open(CAMPGROUND_DATA_PATH, "r", encoding="utf-8") as f:
    campgrounds = json.load(f)

# Ensure logs folder exists
os.makedirs("logs", exist_ok=True)

# Ensure users file exists
if not os.path.exists(USER_DATA_PATH):
    with open(USER_DATA_PATH, "w") as f:
        json.dump([], f)

# Ensure bookings file exists and load
def load_bookings():
    if not os.path.exists(BOOKINGS_DATA_PATH):
        with open(BOOKINGS_DATA_PATH, "w") as f:
            json.dump([], f)
    with open(BOOKINGS_DATA_PATH, "r") as f:
        return json.load(f)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]

        with open(USER_DATA_PATH) as f:
            users = json.load(f)

        user = next((u for u in users if u["username"] == username), None)

        if user:
            session["username"] = user["username"]
            session["user_type"] = user["type"]
            return redirect(url_for("owner_dashboard" if user["type"] == "Owner" else "index"))
        else:
            return render_template("login.html", error="❌ You are not registered with us. Please contact admin.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    if "username" not in session:
        return redirect(url_for("login"))

    camp_id = request.form.get("camp_id")
    from_date = request.form.get("from_date")
    to_date = request.form.get("to_date")

    # Load campgrounds
    with open(CAMPGROUND_DATA_PATH) as f:
        campgrounds = json.load(f)

    selected_camp = next((c for c in campgrounds if c["id"] == camp_id), None)
    if not selected_camp:
        return "Campground not found", 404

    # Load bookings
    bookings = []
    if os.path.exists("bookings.json"):
        with open("bookings.json") as f:
            bookings = json.load(f)

    # ✅ Check if it's already booked
    if not is_available(camp_id, from_date, to_date, bookings):
        return "❌ This campground is already booked for the selected dates.", 400

    # ✅ Check if already in cart for the same date range
    cart = session.get("cart", [])
    for item in cart:
        if (item["camp_id"] == camp_id and
            from_date <= item["to_date"] and
            to_date >= item["from_date"]):
            return "⚠️ Campground already in cart for overlapping dates.", 400

    # ✅ Add to cart
    cart.append({
        "camp_id": camp_id,
        "camp_name": selected_camp["name"],
        "from_date": from_date,
        "to_date": to_date
    })
    session["cart"] = cart

    return redirect(url_for("view_cart"))


@app.route("/cart")
def view_cart():
    if "username" not in session:
        return redirect(url_for("login"))

    cart = session.get("cart", [])
    return render_template("cart.html", cart=cart)

@app.route("/checkout", methods=["POST"])
def checkout():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    cart = session.get("cart", [])

    if not cart:
        return "Cart is empty", 400

    # Load bookings.json
    bookings = []
    if os.path.exists("bookings.json"):
        with open("bookings.json") as f:
            bookings = json.load(f)

    # Load campground data
    with open(CAMPGROUND_DATA_PATH) as f:
        campgrounds = json.load(f)

    # Process each cart item
    for item in cart:
        booking = {
            "username": username,
            "camp_id": item["camp_id"],
            "camp_name": item["camp_name"],
            "from_date": item["from_date"],
            "to_date": item["to_date"]
        }
        bookings.append(booking)

        # Update internal "bookings" of campground
        for camp in campgrounds:
            if camp["id"] == item["camp_id"]:
                camp.setdefault("bookings", [])
                camp["bookings"].append({
                    "from": item["from_date"],
                    "to": item["to_date"]
                })
                break

    # Save updated bookings.json
    with open("bookings.json", "w") as f:
        json.dump(bookings, f, indent=4)

    # Save updated campground.json
    with open(CAMPGROUND_DATA_PATH, "w") as f:
        json.dump(campgrounds, f, indent=4)

    # Clear cart
    session["cart"] = []

    return render_template("checkout_success.html")



@app.route("/search", methods=["GET", "POST"])
def search():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    user_type = session["user_type"]

    # Load user favorites from users.json
    with open(USER_DATA_PATH) as f:
        users = json.load(f)

    user_data = next((u for u in users if u["username"] == username), {})
    user_favorites_names = user_data.get("favorites", [])
    
    with open(CAMPGROUND_DATA_PATH) as f:
        all_camps = json.load(f)

    favorites = [c for c in all_camps if c["name"] in user_favorites_names]
    recommendations = []
    error = None
    query = from_date_str = to_date_str = ""

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        from_date_str = request.form.get("from_date", "").strip()
        to_date_str = request.form.get("to_date", "").strip()

        if not query or not from_date_str or not to_date_str:
            error = "Please fill in all the fields."
        else:
            try:
                from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
                to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()

                if from_date > to_date:
                    error = "Start date cannot be after end date."
                else:
                    prefs = extract_preferences(query)
                    bookings = load_bookings()

                    matched = match_campgrounds(prefs, all_camps, from_date, to_date, bookings)

                    # Round score, add to camp, and build recommendation list
                    for score, camp in matched:
                        camp_copy = camp.copy()
                        camp_copy["match_score"] = round(score, 2)
                        recommendations.append(camp_copy)

                    # ✅ Log the interaction
                    log_interaction(username, query, recommendations)

            except ValueError:
                error = "Invalid date format. Please use YYYY-MM-DD."

    return render_template(
        "home.html",
        username=username,
        user_type=user_type,
        recommendations=recommendations,
        favorites=favorites,
        error=error,
        query=query,
        from_date=from_date_str,
        to_date=to_date_str
    )


@app.route("/owner_dashboard")
def owner_dashboard():
    if session.get("user_type") != "Owner":
        return redirect(url_for("login"))

    username = session["username"]
    with open(CAMPGROUND_DATA_PATH) as f:
        camps = json.load(f)

    owner_camps = [c for c in camps if c.get("owner_id") == username]
    return render_template("owner_dashboard.html", listings=owner_camps)


@app.route("/delete_listing/<name>")
def delete_listing(name):
    with open(CAMPGROUND_DATA_PATH) as f:
        camps = json.load(f)

    camps = [c for c in camps if c["name"] != name]

    with open(CAMPGROUND_DATA_PATH, "w") as f:
        json.dump(camps, f, indent=2)

    return redirect(url_for("owner_dashboard"))


@app.route("/edit_listing/<name>", methods=["GET", "POST"])
def edit_listing(name):
    with open(CAMPGROUND_DATA_PATH) as f:
        camps = json.load(f)

    camp = next((c for c in camps if c["name"] == name), None)

    if request.method == "POST":
        camp["location"] = request.form["location"]
        camp["type"] = request.form["type"]
        camp["activities"] = request.form["activities"]
        camp["status"] = request.form["status"]

        with open(CAMPGROUND_DATA_PATH, "w") as f:
            json.dump(camps, f, indent=2)

        return redirect(url_for("owner_dashboard"))

    return render_template("edit_listing.html", camp=camp)


@app.route("/update_status/<name>")
def update_status(name):
    with open(CAMPGROUND_DATA_PATH) as f:
        camps = json.load(f)

    for camp in camps:
        if camp["name"] == name:
            camp["status"] = "Inactive" if camp["status"] == "Active" else "Active"
            break

    with open(CAMPGROUND_DATA_PATH, "w") as f:
        json.dump(camps, f, indent=2)

    return redirect(url_for("owner_dashboard"))


@app.route("/add_listing", methods=["GET", "POST"])
def add_listing():
    if request.method == "POST":
        new_camp = {
            "name": request.form["name"],
            "location": request.form["location"],
            "type": request.form["type"],
            "activities": request.form["activities"],
            "status": "Active",
            "owner_id": session["username"]
        }

        with open(CAMPGROUND_DATA_PATH) as f:
            camps = json.load(f)

        camps.append(new_camp)

        with open(CAMPGROUND_DATA_PATH, "w") as f:
            json.dump(camps, f, indent=2)

        return redirect(url_for("owner_dashboard"))

    return render_template("add_listing.html")


@app.route("/favorite", methods=["POST"])
def favorite():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    campground_name = request.form.get("campground_name")

    with open(USER_DATA_PATH) as f:
        users = json.load(f)

    for user in users:
        if user["username"] == username:
            user.setdefault("favorites", [])
            if campground_name not in user["favorites"]:
                user["favorites"].append(campground_name)
            break

    with open(USER_DATA_PATH, "w") as f:
        json.dump(users, f, indent=2)

    return redirect(url_for("index"))


@app.route("/remove_favorite", methods=["POST"])
def remove_favorite():
    if "username" not in session:
        return jsonify({"status": "error", "message": "Not logged in"}), 401

    username = session["username"]
    campground_name = request.json.get("name")

    with open(USER_DATA_PATH) as f:
        users = json.load(f)

    for user in users:
        if user["username"] == username:
            user.setdefault("favorites", [])
            user["favorites"] = [fav for fav in user["favorites"] if fav != campground_name]
            break

    with open(USER_DATA_PATH, "w") as f:
        json.dump(users, f, indent=2)

    return jsonify({"status": "success"})


@app.route("/", methods=["GET", "POST"])
def index():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]

    with open(USER_DATA_PATH) as f:
        users = json.load(f)

    for user in users:
        if user["username"] == username:
            user.setdefault("favorites", [])
            user.setdefault("history", [])
            break

    with open(USER_DATA_PATH, "w") as f:
        json.dump(users, f, indent=2)

    with open(CAMPGROUND_DATA_PATH) as f:
        campgrounds = json.load(f)

    user_data = next((u for u in users if u["username"] == username), {"favorites": [], "history": []})

    favorites = [
        c for c in campgrounds
        if any(c["name"].lower() == fav.lower() for fav in user_data["favorites"])
    ]

    recommendations = []
    query = ""
    error = None

    if request.method == "POST":
        query = request.form.get("query", "").strip()

        if not query:
            error = "⚠️ Please enter some preferences to get recommendations."
        else:
            prefs = extract_preferences(query)

            if not any([prefs.get("location"), prefs.get("type"), prefs.get("activities"), prefs.get("amenities")]):
                error = "❗ I couldn't understand your input. Please provide valid input."
            else:
                user_data["history"].append(query)
                with open(USER_DATA_PATH, "w") as f:
                    json.dump(users, f, indent=2)

                results = match_campgrounds(prefs, campgrounds)
                for camp in results:
                    camp["match_score"] = compute_score(camp, prefs)

                recommendations = sorted(results, key=lambda x: x["match_score"], reverse=True)[:3]
                log_interaction(username, query, recommendations)

    return render_template(
        "home.html",
        username=username,
        favorites=favorites,
        recommendations=recommendations,
        query=query,
        error=error
    )


@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    with open(USER_DATA_PATH) as f:
        users = json.load(f)

    user_data = next((u for u in users if u["username"] == username), {"favorites": [], "history": []})

    return render_template("profile.html", favorites=user_data["favorites"], history=user_data["history"])


def compute_score(camp, prefs):
    score = 0
    if prefs["location"] and prefs["location"] in camp["location"].lower():
        score += 4
    if prefs["type"] and prefs["type"] in camp["type"].lower():
        score += 1
    score += len(set(prefs["activities"]) & set([a.lower().strip() for a in camp.get("activities", [])]))
    score += len(set(prefs["amenities"]) & set([a.lower().strip() for a in camp.get("amenities", [])]))
    return score


def log_interaction(username, query, results):
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    today = now.strftime("%Y-%m-%d")
    filename = f"logs/log_{today}.txt"

    result_summary = "; ".join(
        f"{camp['id']} ({camp['location']}) - Score: {camp.get('match_score', 0)}" for camp in results
    )

    with open(filename, "a", encoding="utf-8") as log_file:
        log_file.write(f"{timestamp} | User: {username} | Query: {query} | Matches: {result_summary}\n")


if __name__ == "__main__":
    app.run(debug=True)
