from __future__ import annotations

from functools import wraps
from typing import Any, Dict, List, Optional

import requests
from flask import Flask, flash, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-change-me"

BACKEND_BASE_URL = "http://localhost:5000"

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}


def backend_get(path: str) -> Any:
    try:
        response = requests.get(f"{BACKEND_BASE_URL}{path}", timeout=4)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {"error": str(exc)}


def backend_post(path: str, payload: Dict[str, Any]) -> Any:
    try:
        response = requests.post(f"{BACKEND_BASE_URL}{path}", json=payload, timeout=4)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {"error": str(exc)}


def get_user_context() -> Dict[str, str] | None:
    user = session.get("user")
    if isinstance(user, dict) and user.get("user_id") and user.get("username"):
        profile = get_profile()
        username = profile.get("name") if profile and profile.get("name") else user["username"]
        return {"user_id": str(user["user_id"]), "username": str(username)}
    return None


def get_profile() -> Optional[Dict[str, Any]]:
    profile = session.get("profile")
    return profile if isinstance(profile, dict) else None


def has_complete_profile() -> bool:
    profile = get_profile()
    if not profile:
        return False
    required = ["height_cm", "weight_kg", "age", "gender", "activity"]
    return all(profile.get(key) not in (None, "") for key in required)


def build_health_metrics(profile: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not profile:
        return {"bmi": "--", "daily_need": "--"}

    try:
        height_cm = float(profile.get("height_cm", 0))
        weight_kg = float(profile.get("weight_kg", 0))
        age = int(float(profile.get("age", 0)))
    except (TypeError, ValueError):
        return {"bmi": "--", "daily_need": "--"}

    if height_cm <= 0 or weight_kg <= 0 or age <= 0:
        return {"bmi": "--", "daily_need": "--"}

    bmi = round(weight_kg / ((height_cm / 100) ** 2), 2)
    gender = str(profile.get("gender", "male")).lower()
    activity = str(profile.get("activity", "moderate"))
    activity_factor = ACTIVITY_MULTIPLIERS.get(activity, 1.55)

    if gender == "female":
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    elif gender == "male":
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        # Neutral fallback midway between male/female constants.
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 78

    daily_need = int(round(bmr * activity_factor))
    return {"bmi": bmi, "daily_need": daily_need}


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not get_user_context():
            return redirect(url_for("login_page"))
        return view_func(*args, **kwargs)

    return wrapped_view


def profile_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not has_complete_profile():
            return redirect(url_for("profile_page"))
        return view_func(*args, **kwargs)

    return wrapped_view


def compute_daily_summary(meals: List[Dict[str, Any]]) -> Dict[str, int]:
    calories = sum(int(float(item.get("calories", 0) or 0)) for item in meals)
    protein = sum(int(float(item.get("protein", 0) or 0)) for item in meals)
    water = sum(int(float(item.get("water", 0) or 0)) for item in meals)
    return {"calories": calories, "protein": protein, "water": water}


@app.route("/")
@app.route("/add-meal")
@login_required
@profile_required
def add_meal_page() -> str:
    user = get_user_context()
    if not user:
        return redirect(url_for("login_page"))
    meals_response = backend_get(f"/api/meals/{user['user_id']}")
    meals: List[Dict[str, Any]] = meals_response if isinstance(meals_response, list) else []
    summary = compute_daily_summary(meals)
    metrics = build_health_metrics(get_profile())
    return render_template(
        "add_meal.html",
        user=user,
        meals=meals,
        summary=summary,
        metrics=metrics,
        active_page="add-meal",
    )


@app.post("/add-meal")
@login_required
@profile_required
def add_meal_submit() -> str:
    user = get_user_context()
    if not user:
        return redirect(url_for("login_page"))
    payload = {
        "userId": user["user_id"],
        "food": request.form.get("food", ""),
        "calories": request.form.get("calories", 0),
        "protein": request.form.get("protein", 0),
        "carbs": request.form.get("carbs", 0),
        "fat": request.form.get("fat", 0),
        "water": request.form.get("water", 0),
    }
    result = backend_post("/api/meals/add", payload)
    if "error" in result:
        flash(f"Could not add meal: {result['error']}", "error")
    else:
        flash("Meal added successfully.", "success")

    return redirect(url_for("add_meal_page"))


@app.route("/analytics")
@login_required
@profile_required
def analytics_page() -> str:
    user = get_user_context()
    if not user:
        return redirect(url_for("login_page"))
    meals_response = backend_get(f"/api/analytics/{user['user_id']}")
    meals = meals_response if isinstance(meals_response, list) else []
    summary = compute_daily_summary(meals)
    metrics = build_health_metrics(get_profile())
    return render_template(
        "analytics.html", user=user, meals=meals, summary=summary, metrics=metrics, active_page="analytics"
    )


@app.route("/recommendation")
@login_required
@profile_required
def recommendation_page() -> str:
    user = get_user_context()
    if not user:
        return redirect(url_for("login_page"))
    recommendation = backend_get(f"/api/recommend/{user['user_id']}")
    metrics = build_health_metrics(get_profile())
    return render_template(
        "recommendation.html",
        user=user,
        recommendation=recommendation,
        metrics=metrics,
        active_page="recommendation",
    )


@app.route("/coach", methods=["GET", "POST"])
@login_required
@profile_required
def coach_page() -> str:
    user = get_user_context()
    if not user:
        return redirect(url_for("login_page"))
    reply = None
    if request.method == "POST":
        user_message = request.form.get("message", "")
        result = backend_post("/api/coach", {"message": user_message})
        reply = result.get("reply") if isinstance(result, dict) else None
        if isinstance(result, dict) and "error" in result:
            flash(f"Coach service error: {result['error']}", "error")
    metrics = build_health_metrics(get_profile())
    return render_template("coach.html", user=user, coach_reply=reply, metrics=metrics, active_page="coach")


@app.route("/health-diet", methods=["GET", "POST"])
@login_required
@profile_required
def health_page() -> str:
    user = get_user_context()
    if not user:
        return redirect(url_for("login_page"))
    diet_result = None
    if request.method == "POST":
        condition = request.form.get("condition", "")
        result = backend_post("/api/health", {"condition": condition})
        diet_result = result.get("diet") if isinstance(result, dict) else None
        if isinstance(result, dict) and "error" in result:
            flash(f"Health service error: {result['error']}", "error")
    metrics = build_health_metrics(get_profile())
    return render_template("health.html", user=user, diet_result=diet_result, metrics=metrics, active_page="health")


@app.route("/rewards")
@login_required
@profile_required
def rewards_page() -> str:
    user = get_user_context()
    if not user:
        return redirect(url_for("login_page"))
    rewards = backend_get(f"/api/gamify/{user['user_id']}")
    metrics = build_health_metrics(get_profile())
    return render_template("rewards.html", user=user, rewards=rewards, metrics=metrics, active_page="rewards")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile_page() -> str:
    user = get_user_context()
    if not user:
        return redirect(url_for("login_page"))

    existing_profile = get_profile() or {}

    if request.method == "POST":
        name = (request.form.get("name") or user["username"]).strip()
        age = request.form.get("age")
        gender = request.form.get("gender")
        height_cm = request.form.get("height_cm")
        weight_kg = request.form.get("weight_kg")
        activity = request.form.get("activity")

        profile_data = {
            "name": name,
            "age": age,
            "gender": gender,
            "height_cm": height_cm,
            "weight_kg": weight_kg,
            "activity": activity,
        }

        metrics = build_health_metrics(profile_data)
        if metrics["bmi"] == "--":
            flash("Please enter valid profile values to calculate BMI.", "error")
            return render_template(
                "profile.html",
                user=user,
                profile=profile_data,
                metrics=build_health_metrics(existing_profile),
                active_page="profile",
            )

        session["profile"] = profile_data
        flash("Profile saved. BMI and daily need are updated.", "success")
        return redirect(url_for("add_meal_page"))

    return render_template(
        "profile.html",
        user=user,
        profile=existing_profile,
        metrics=build_health_metrics(existing_profile),
        active_page="profile",
    )


@app.route("/login", methods=["GET", "POST"])
def login_page() -> str:
    if get_user_context():
        return redirect(url_for("add_meal_page"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""
        if not email:
            flash("Email is required.", "error")
            return render_template("login.html")

        result = backend_post("/api/auth/login", {"email": email, "password": password})
        user_record = result if isinstance(result, dict) else None

        # Backend starts with empty in-memory users; auto-register keeps first run smooth.
        if not user_record or not user_record.get("id"):
            create_result = backend_post(
                "/api/auth/register",
                {"name": email.split("@")[0], "email": email, "password": password},
            )
            if isinstance(create_result, dict) and create_result.get("id"):
                user_record = create_result
                flash("Account created and logged in.", "success")

        if isinstance(user_record, dict) and user_record.get("id"):
            username = user_record.get("name") or email.split("@")[0] or "User"
            session["user"] = {"user_id": str(user_record["id"]), "username": str(username)}
            if not has_complete_profile():
                return redirect(url_for("profile_page"))
            return redirect(url_for("add_meal_page"))

        flash("Login failed. Please verify backend is running and try again.", "error")

    return render_template("login.html")


@app.post("/logout")
def logout() -> str:
    session.clear()
    return redirect(url_for("login_page"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
