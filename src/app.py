import os
import requests
from flask import Flask, render_template, request
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

def get_weather(city: str):
    """
    Fetch weather data for `city` from OpenWeatherMap.
    Returns a dict with keys:
      - city
      - temperature
      - description
      - humidity
    or None if not found / error.
    """
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise RuntimeError("Missing API_KEY in environment")

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={api_key}&units=metric"
    )
    resp = requests.get(url)
    data = resp.json()

    # If API returns an error or missing data
    if resp.status_code != 200 or "main" not in data:
        return None

    # Successful response
    return {
        "city": city,
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"],
        "humidity": data["main"]["humidity"],
    }

@app.route("/", methods=["GET", "POST"])
def index():
    weather = None
    error = None

    if request.method == "POST":
        city = request.form.get("city", "").strip()
        if not city:
            error = "Please enter a city name."
        else:
            try:
                result = get_weather(city)
            except RuntimeError as e:
                error = str(e)
            else:
                if result:
                    weather = result
                else:
                    error = "City not found."

    return render_template("index.html", weather=weather, error=error)

if __name__ == "__main__":
    # Use PORT from environment (Heroku/Render), default to 5000 for local
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
