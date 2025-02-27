import sqlite3
import json
from flask import Flask, request, jsonify, render_template, g
from datetime import datetime
import os

# Path to your SQLite database file
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'metrics.db')

app = Flask(__name__)

def get_db():
    """Return a database connection, creating one if necessary."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Allows accessing columns by name
    return db

def init_db():
    """Initialise the database with the required table."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS MetricLog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            metric_type TEXT,
            timestamp TEXT,
            data TEXT
        )
    ''')
    db.commit()
    print("Database initialized")

@app.teardown_appcontext
def close_connection(exception):
    """Close the database connection at the end of the request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/api/metrics', methods=['POST'])
def receive_metrics():
    """
    Receives JSON data from the monitoring agent. Expected JSON structure:
    {
        "device_id": "my_pc_01",
        "metrics": {
            "system": { "processes": 123, "ram_usage": 45.6 },
            "weather": { "temperature": 15, "condition": "Cloudy" }
        }
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    device_id = data.get('device_id', 'unknown')
    metrics = data.get('metrics', {})
    timestamp = datetime.utcnow().isoformat()

    db = get_db()
    cursor = db.cursor()

    # Save system metrics if provided.
    if 'system' in metrics:
        system_data = json.dumps(metrics['system'])
        cursor.execute('''
            INSERT INTO MetricLog (device_id, metric_type, timestamp, data)
            VALUES (?, ?, ?, ?)
        ''', (device_id, 'system', timestamp, system_data))

    # Save weather metrics if provided.
    if 'weather' in metrics:
        weather_data = json.dumps(metrics['weather'])
        cursor.execute('''
            INSERT INTO MetricLog (device_id, metric_type, timestamp, data)
            VALUES (?, ?, ?, ?)
        ''', (device_id, 'weather', timestamp, weather_data))

    db.commit()
    return jsonify({'status': 'success'}), 200

@app.route('/api/metrics/logs', methods=['GET'])
def get_logs():
    """
    Returns the latest 100 log entries, ordered by timestamp (most recent first).
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT id, device_id, metric_type, timestamp, data 
        FROM MetricLog 
        ORDER BY timestamp DESC 
        LIMIT 100
    ''')
    rows = cursor.fetchall()
    logs = []
    for row in rows:
        try:
            # Convert the stored JSON string back to a Python dictionary.
            data_obj = json.loads(row['data'])
        except Exception:
            data_obj = row['data']
        logs.append({
            'id': row['id'],
            'device_id': row['device_id'],
            'metric_type': row['metric_type'],
            'timestamp': row['timestamp'],
            'data': data_obj
        })
    return jsonify(logs), 200

@app.route('/dashboard')
def dashboard():
    """Renders the dashboard UI."""
    return render_template('dashboard.html')

@app.route('/test')
def test():
    """Renders a test page to send sample data to the API."""
    return render_template('test.html')

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run()
