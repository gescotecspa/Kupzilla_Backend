from app import db
from datetime import datetime, timezone
from sqlalchemy.orm import validates

class AppVersion(db.Model):
    __tablename__ = 'app_versions'

    id = db.Column(db.Integer, primary_key=True)
    version_number = db.Column(db.String(20), nullable=False)
    app_type = db.Column(db.String(50), nullable=False)
    platform = db.Column(db.String(50), nullable=False) 
    release_date = db.Column(db.Date, nullable=False, default=datetime.now(timezone.utc).date) 
    #Representa la fecha oficial en la que la versión de la aplicación fue prevista a lanzar o lanzada para los usuarios.
    download_url = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_required = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    @validates('platform')
    def validate_platform(self, key, value):
        allowed_platforms = ['iOS', 'Android']
        if value not in allowed_platforms:
            raise ValueError(f"Platform must be one of {allowed_platforms}")
        return value

    @validates('app_type')
    def validate_app_type(self, key, value):
        allowed_app_types = ['tourist', 'associated']
        if value not in allowed_app_types:
            raise ValueError(f"App type must be one of {allowed_app_types}")
        return value
    # Método para serializar el modelo
    def serialize(self):
        return {
            "id": self.id,
            "version_number": self.version_number,
            "app_type": self.app_type,
            "platform": self.platform,
            "release_date": self.release_date.isoformat() if self.release_date else None,
            "download_url": self.download_url,
            "notes": self.notes,
            "is_active": self.is_active,
            "is_required": self.is_required,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<AppVersion {self.version_number} ({self.platform})>'
