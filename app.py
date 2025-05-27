from flask import Flask, render_template, request, jsonify, Response
from weather_api import search_locations, get_weather_by_coords, get_weather_forecast, get_hourly_forecast
from db import insert_weather_log, get_all_logs, update_weather_log, delete_weather_log, get_db 
import csv
from io import StringIO
import requests
from config import YOUTUBE_API_KEY

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_location')
def search_location():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    try:
        if ',' in q:
            lat, lon = map(float, q.split(','))
            return jsonify([{
                "name": f"Coordinates",
                "lat": lat,
                "lon": lon,
                "country": "",
                "state": ""
            }])
    except ValueError:
        pass
    results = search_locations(q)
    return jsonify(results)

@app.route('/get_weather')
def get_weather():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify({"error": "Missing latitude or longitude"})
    weather = get_weather_by_coords(lat, lon)

    if "name" in weather and "main" in weather:
        try:
            insert_weather_log({
                "location": weather["name"],
                "lat": float(lat),
                "lon": float(lon),
                "temp": weather["main"]["temp"],
                "humidity": weather["main"]["humidity"],
                "wind_speed": weather["wind"]["speed"],
                "description": weather["weather"][0]["description"],
                "icon": weather["weather"][0]["icon"]
            })
        except Exception as e:
            print("Failed:", e)

    return jsonify(weather)

@app.route('/get_forecast')
def get_forecast():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify({"error": "Missing latitude or longitude"})
    forecast = get_weather_forecast(lat, lon)
    return jsonify(forecast)

@app.route('/get_hourly')
def get_hourly():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify({"error": "Missing lat/lon"})
    
    data = get_hourly_forecast(lat, lon)
    return jsonify(data)

@app.route('/logs')
def show_logs():
    logs = get_all_logs()
    return jsonify(logs)

@app.route('/update_log', methods=['POST'])
def update_log():
    data = request.json
    try:
        update_weather_log(data['id'], data['description'], data['temperature'])
        return jsonify({"message": "Log updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/delete_log', methods=['POST'])
def delete_log():
    data = request.json
    try:
        delete_weather_log(data['id'])
        return jsonify({"message": "Log deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/history')
def history_page():
    return render_template('history.html')

@app.route('/api/history')
def api_history():
    location = request.args.get('location', '')
    start = request.args.get('start', '')
    end = request.args.get('end', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    db = get_db()
    cursor = db.cursor()
    
    query = "SELECT * FROM weather_logs WHERE 1=1"
    count_query = "SELECT COUNT(*) AS count FROM weather_logs WHERE 1=1"
    params = []

    if location:
        query += " AND location LIKE %s"
        count_query += " AND location LIKE %s"
        params.append(f"%{location}%")

    if start:
        query += " AND recorded_at >= %s"
        count_query += " AND recorded_at >= %s"
        params.append(start)

    if end:
        query += " AND recorded_at <= %s"
        count_query += " AND recorded_at <= %s"
        params.append(end + " 23:59:59")

    cursor.execute(count_query, params)
    result = cursor.fetchone()
    total = result['count'] if result else 0

    query += " ORDER BY recorded_at DESC LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()

    return jsonify({
        "records": rows,
        "total_pages": (total + per_page - 1) // per_page,
        "current_page": page
    })

@app.route('/api/history/<int:record_id>', methods=['PUT'])
def update_history(record_id):
    data = request.get_json()
    field = data.get('field')
    value = data.get('value')

    if field not in ['location', 'temperature', 'humidity']:
        return jsonify({"error": "Invalid field"}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"UPDATE weather_logs SET {field} = %s WHERE id = %s", (value, record_id))
    db.commit()
    return jsonify({"status": "updated"})

@app.route('/api/history/<int:record_id>', methods=['DELETE'])
def delete_history(record_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM weather_logs WHERE id = %s", (record_id,))
    db.commit()
    return jsonify({"status": "deleted"})

@app.route('/api/history/export')
def export_csv():
    location = request.args.get('location', '')
    start = request.args.get('start', '')
    end = request.args.get('end', '')

    db = get_db()
    cursor = db.cursor()

    query = "SELECT * FROM weather_logs WHERE 1=1"
    params = []

    if location:
        query += " AND location LIKE %s"
        params.append(f"%{location}%")
    if start:
        query += " AND recorded_at >= %s"
        params.append(start)
    if end:
        query += " AND recorded_at <= %s"
        params.append(end + " 23:59:59")

    cursor.execute(query, params)
    rows = cursor.fetchall()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(rows[0].keys() if rows else ["No data"])
    for row in rows:
        writer.writerow(row.values())

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=weather_history.csv"}
    )

@app.route('/api/youtube_videos')
def youtube_videos():
    location = request.args.get('location', '')
    if not location:
        return jsonify({"error": "Missing location"}), 400

    search_url = 'https://www.googleapis.com/youtube/v3/search'
    params = {
        'part': 'snippet',
        'q': location,
        'type': 'video',
        'maxResults': 5,
        'key': YOUTUBE_API_KEY,
    }

    resp = requests.get(search_url, params=params)
    if resp.status_code != 200:
        return jsonify({"error": "YouTube API error"}), 500

    videos = []
    data = resp.json()
    for item in data.get('items', []):
        videos.append({
            'videoId': item['id']['videoId'],
            'title': item['snippet']['title'],
            'thumbnail': item['snippet']['thumbnails']['default']['url']
        })

    return jsonify(videos)

if __name__ == '__main__':
    app.run(debug=True)