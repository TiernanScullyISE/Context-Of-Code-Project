from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class MetricLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50))
    metric_type = db.Column(db.String(50))  # 'system' or 'weather'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    data = db.Column(db.JSON)  # Note: In SQLite this may be stored as TEXT

    def __repr__(self):
        return f'<MetricLog {self.metric_type} at {self.timestamp}>'
