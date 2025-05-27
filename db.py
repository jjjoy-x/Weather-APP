import pymysql
from datetime import datetime

connection= pymysql.connect(
        host='localhost',
        user='root',
        password='XINGyq300400',
        database='weather_app',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def get_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='XINGyq300400',
        database='weather_app',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# Create
def insert_weather_log(data):
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO weather_logs (
                    location, latitude, longitude, temperature,
                    humidity, wind_speed, description, icon
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                data['location'],
                data['lat'],
                data['lon'],
                data['temp'],
                data['humidity'],
                data['wind_speed'],
                data['description'],
                data['icon']
            ))
        connection.commit()

# Read
def get_all_logs(limit=50):
    
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM weather_logs ORDER BY recorded_at DESC LIMIT %s", (limit,))
            return cursor.fetchall()

# Update
def update_weather_log(log_id, description, temp):

        with connection.cursor() as cursor:
            sql = "UPDATE weather_logs SET description=%s, temperature=%s WHERE id=%s"
            cursor.execute(sql, (description, temp, log_id))
        connection.commit()
    
# Delete
def delete_weather_log(log_id):
        with connection.cursor() as cursor:
            sql = "DELETE FROM weather_logs WHERE id=%s"
            cursor.execute(sql, (log_id,))
