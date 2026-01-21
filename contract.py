from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Contract(db.Model):
    __tablename__ = 'contracts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    original_filename = db.Column(db.String(255))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    extracted_text = db.Column(db.Text)
    sla_data = db.Column(db.Text)  # JSON stored as text
    fairness_score = db.Column(db.Float)
    vehicle_vin = db.Column(db.String(50))
    
    def set_sla_data(self, data):
        self.sla_data = json.dumps(data)
    
    def get_sla_data(self):
        if self.sla_data:
            return json.loads(self.sla_data)
        return {}
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.original_filename,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'fairness_score': self.fairness_score,
            'vehicle_vin': self.vehicle_vin,
            'sla_data': self.get_sla_data()
        }