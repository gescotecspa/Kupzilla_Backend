from app import db

class TouristPoint(db.Model):
    __tablename__ = 'tourist_points'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000))
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    images = db.relationship('Image', backref='tourist_point', lazy=True)
    ratings = db.relationship('Rating', back_populates='tourist_point', lazy=True)

    status_id = db.Column(db.Integer, db.ForeignKey('statuses.id'), nullable=False)
    status = db.relationship('Status', backref='tourist_points')

    def serialize(self):
        average_rating = None
        if self.ratings:
            average_rating = sum(r.rating for r in self.ratings) / len(self.ratings)

        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'images': [image.serialize() for image in self.images],
            'average_rating': average_rating,
            'status': self.status.serialize() if self.status else None
        }

class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255), nullable=False)
    tourist_point_id = db.Column(db.Integer, db.ForeignKey('tourist_points.id'), nullable=False)
    def serialize(self):
        return {
            'id': self.id,
            'image_path': self.image_path
        }

class Rating(db.Model):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(1000))
    tourist_point_id = db.Column(db.Integer, db.ForeignKey('tourist_points.id'), nullable=False)
    tourist_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=True)
    
    # Relación con User (tabla 'users')
    tourist = db.relationship('User', backref='ratings')
    tourist_point = db.relationship('TouristPoint', back_populates='ratings', lazy=True) 
    status_id = db.Column(db.Integer, db.ForeignKey('statuses.id'), nullable=True)
    status = db.relationship('Status', backref='ratings')
    
    def serialize(self):
        return {
            'id': self.id,
            'tourist_point_id': self.tourist_point_id,
            'tourist_point_title': self.tourist_point.title if self.tourist_point else None,
            'tourist_id': self.tourist_id,
            'tourist_first_name': self.tourist.first_name if self.tourist else None, 
            'tourist_image_url': self.tourist.image_url if self.tourist else None, 
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'status': self.status.serialize() if self.status else None,
        }

    __table_args__ = (
        db.UniqueConstraint('tourist_point_id', 'tourist_id', name='_tourist_point_tourist_uc'),
    )