from app import db
from datetime import datetime
import pytz

class TermsAndConditions(db.Model):
    __tablename__ = 'terms_and_conditions'

    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(10), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<TermsAndConditions {self.version}>'

    def serialize(self):
        local_tz = pytz.timezone('America/Santiago')
        local_created_at = self.created_at.replace(tzinfo=pytz.utc).astimezone(local_tz)
        return {
            'id': self.id,
            'version': self.version,
            'created_at': local_created_at.strftime('%Y-%m-%dT%H:%M:%S %z'),
            'content': self.content
        }