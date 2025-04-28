from app import db
from datetime import datetime, timezone

class ContactContent(db.Model):
    __tablename__ = 'contact_contents'

    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(5), nullable=False)
    html_content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def serialize(self):
        return {
            'id': self.id,
            'language': self.language,
            'html_content': self.html_content,
            'created_at': self.created_at.isoformat()
        }