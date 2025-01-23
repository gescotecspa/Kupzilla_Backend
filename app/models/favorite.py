# favorite.py
from app import db

class Favorite(db.Model):
    __tablename__ = 'favorites'

    user_id = db.Column(db.Integer, db.ForeignKey('tourists.user_id'), primary_key=True)
    promotion_id = db.Column(db.Integer, db.ForeignKey('promotions.promotion_id'), primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    tourist = db.relationship('Tourist', back_populates='favorites')
    promotion = db.relationship('Promotion', back_populates='favorites')

    def serialize(self):
        return {
            "user_id": self.user_id,
            "promotion_id": self.promotion_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
