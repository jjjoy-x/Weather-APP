# Weather App with History Management

A Flask-based weather application that fetches current weather and forecast data from OpenWeatherMap API, stores search history in MySQL, and provides a web UI for search, history viewing, filtering, editing, deleting, and exporting data.

## Features

- Search weather by city name, ZIP/postal code, GPS coordinates, or landmarks
- Auto-complete and location suggestions
- Current weather + 5-day forecast + hourly temperature chart
- Store search results history in MySQL database
- View search history with pagination, date range, and location filtering
- Edit and delete historical records directly in the web interface
- Export history data to CSV format
- Display related YouTube videos for searched locations

## Tech Stack

- Backend: Python, Flask
- Frontend: HTML, CSS, JavaScript, Chart.js
- Database: MySQL (using PyMySQL driver)
- APIs: OpenWeatherMap, YouTube Data API v3

## Setup & Installation

### Prerequisites

- Python 3.7+
- MySQL Server
- [OpenWeatherMap API key](https://openweathermap.org/api)
- [Google YouTube API key](https://console.cloud.google.com/apis/credentials)

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/weather-app.git
cd weather-app
```

### 2. Create and configure MySQL database

```sql
CREATE DATABASE weather_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE weather_app;

CREATE TABLE weather_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  location VARCHAR(255),
  latitude DOUBLE,
  longitude DOUBLE,
  temperature FLOAT,
  humidity INT,
  wind_speed FLOAT,
  description VARCHAR(255),
  icon VARCHAR(50),
  recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API keys

Edit config.py

```Python
WEATHER_API_KEY = 'your_openweathermap_api_key'
YOUTUBE_API_KEY = 'your_youtube_api_key'
```

### 5. Run the Flask app

```bash
python app.py
```

App will be available at http://127.0.0.1:5000

### Usage

- Use the search box on the main page to find weather for any location.

- Click "View History" to see your past searches.

- Filter history by location and date range.

- Edit temperature, humidity, or location fields directly in the table.

- Delete unwanted records with the delete button.

- Export filtered records as a CSV file.

### File Structure

├── app.py              # Flask backend routes and logic
├── db.py               # Database connection and CRUD functions
├── weather_api.py      # OpenWeatherMap API wrappers
├── config.py           # API keys and config
├── requirements.txt    # Python dependencies
├── templates/
│   ├── index.html      # Main page template
│   └── history.html    # History page template
└── static/
    └── script.js       # Frontend JavaScript logic

### Note

- Ensure your MySQL user has permissions to create and modify tables.

- API rate limits apply for OpenWeatherMap and YouTube APIs.

- For production deployment, configure environment variables and use a production-ready WSGI server.
