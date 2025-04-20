import os
import requests
from flask import Flask, render_template, request
from dotenv import load_dotenv

load_dotenv()  # reads .env in project root

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    weather = None
    error = None

    if request.method == 'POST':
        city = request.form.get('city', '').strip()
        if not city:
            error = "Please enter a city name."
        else:
            api_key = os.getenv('API_KEY')
            if not api_key:
                error = "API_KEY not set in environment."
            else:
                # Call OpenWeatherMap API
                url = (
                  f"http://api.openweathermap.org/data/2.5/weather"
                  f"?q={city}&appid={api_key}&units=metric"
                )
                resp = requests.get(url).json()
                if resp.get('main'):
                    weather = {
                        'city': city,
                        'temperature': resp['main']['temp'],
                        'description': resp['weather'][0]['description'],
                        'humidity': resp['main']['humidity']
                    }
                else:
                    # show API error message if provided
                    error = resp.get('message', 'City not found.')

    return render_template('index.html', weather=weather, error=error)

if __name__ == '__main__':
    # pick up PORT from env (Render/Heroku sets this), default 5000
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
