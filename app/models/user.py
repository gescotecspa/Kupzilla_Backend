from app import db
from app.models.status import Status 
from datetime import datetime
import pytz

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(250), nullable=False)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=True)
    country = db.relationship('Country', backref='users')

    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=True)
    city = db.relationship('City', backref='users')
    
    birth_date = db.Column(db.String(10))
    email = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(20))
    gender = db.Column(db.String(10))
    status_id = db.Column(db.Integer, db.ForeignKey('statuses.id'), nullable=False)
    status = db.relationship('Status', backref='users')
    subscribed_to_newsletter = db.Column(db.Boolean)
    image_url = db.Column(db.String(250))
    reset_code = db.Column(db.String(8), nullable=True)
    reset_code_expiration = db.Column(db.DateTime, nullable=True)
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))
    
    terms_id = db.Column(db.Integer, db.ForeignKey('terms_and_conditions.id'), nullable=True)
    terms = db.relationship('TermsAndConditions', backref='users')
    terms_accepted_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    
    app_version = db.Column(db.String(20), nullable=True)  # Versión de la app
    platform = db.Column(db.String(50), nullable=True)     # ej. Android, iOS
    last_login_at = db.Column(db.DateTime, nullable=True)
    registration_date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    
    def serialize(self):
        local_tz = pytz.timezone('America/Santiago')
    
        if self.terms_accepted_at is not None:
            terms_accepted_at = self.terms_accepted_at.replace(tzinfo=pytz.utc).astimezone(local_tz)
        else:
            terms_accepted_at = None 
        
        return {
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'country': self.country.serialize() if self.country else None,
            'city': self.city.serialize() if self.city else None,
            'birth_date': self.birth_date,
            'email': self.email,
            'phone_number': self.phone_number,
            'gender': self.gender,
            'status': self.status.serialize() if self.status else None,
            'subscribed_to_newsletter': self.subscribed_to_newsletter,
            'image_url': self.image_url,
            "roles": [role.serialize() for role in self.roles],
            'terms': self.terms.serialize() if self.terms else None,
            'terms_accepted_at': terms_accepted_at.strftime('%Y-%m-%dT%H:%M:%S %z') if terms_accepted_at else None,
            'app_version': self.app_version,
            'platform': self.platform,
            'last_login_at': self.last_login_at.strftime('%Y-%m-%dT%H:%M:%S %z') if self.last_login_at else None,
            'user_registration_date': self.registration_date.strftime('%Y-%m-%dT%H:%M:%S %z') if self.registration_date else None
        }