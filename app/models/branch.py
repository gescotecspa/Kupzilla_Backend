from app import db
from sqlalchemy import func
from app.models.branch_rating import BranchRating
from app.models.status import Status
from sqlalchemy import or_

class Branch(db.Model):
    __tablename__ = 'branches'

    branch_id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey('partner_details.user_id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('statuses.id'), nullable=False)  
    image_url = db.Column(db.String(255)) 
    partner = db.relationship('Partner', back_populates='branches')
    promotions = db.relationship('Promotion', backref='branch', lazy=True, cascade='all, delete-orphan')
    status = db.relationship('Status') 

    ratings = db.relationship('BranchRating', back_populates='branch', lazy=True)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=True)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=True)
    country = db.relationship('Country', backref='branches')
    city = db.relationship('City', backref='branches')
    images = db.relationship('BranchImage', back_populates='branch', cascade="all, delete-orphan")

    def average_rating(self):
        # Calcular el promedio de las calificaciones de esta sucursal
        approved_status = Status.query.filter_by(name='approved').first()
        pending_status = Status.query.filter_by(name='pending').first()
        
        avg_rating = db.session.query(func.avg(BranchRating.rating)).filter(
        BranchRating.branch_id == self.branch_id,
        or_(
            BranchRating.status_id == approved_status.id,
            BranchRating.status_id == pending_status.id,
            BranchRating.status_id.is_(None)
        )
    ).scalar()
        
        return round(avg_rating, 1) if avg_rating is not None else 0.0
    
    def serialize(self):
        return {
            "branch_id": self.branch_id,
            "partner_id": self.partner_id,
            "name": self.name,
            "description": self.description,
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "status": self.status.serialize() if self.status else None,
            "image_url": self.image_url,
            "images": [image.serialize() for image in self.images],
            "average_rating": self.average_rating(),
            "country": self.country.serialize() if self.country else None,
            "city": self.city.serialize() if self.city else None
        }

    def __repr__(self):
        return f'<Branch {self.name}>'
    
class BranchImage(db.Model):
    __tablename__ = 'branch_images'

    image_id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.branch_id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    is_main = db.Column(db.Boolean, default=False)
    branch = db.relationship('Branch', back_populates='images')
    
    def serialize(self):
        return {
            "image_id": self.image_id,
            "image_url": self.image_url,
            "is_main": self.is_main
        }