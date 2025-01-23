from app import db

# Definición de la tabla de asociación para SQLAlchemy
tourist_categories = db.Table('tourist_categories',
    db.Column('user_id', db.Integer, db.ForeignKey('tourists.user_id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.category_id'), primary_key=True)
)

class Tourist(db.Model):
    __tablename__ = 'tourists'

    user_id = db.Column(db.Integer, primary_key=True)
    origin = db.Column(db.String(255))
    birthday = db.Column(db.Date)
    gender = db.Column(db.String(50))
    categories = db.relationship('Category', secondary=tourist_categories, lazy='dynamic')
    favorites = db.relationship('Favorite', back_populates='tourist', cascade='all, delete-orphan', overlaps='favorite_promotions')

    def serialize(self):
        return {
            "user_id": self.user_id,
            "origin": self.origin,
            "birthday": self.birthday.isoformat() if self.birthday else None,
            "gender": self.gender,
            "categories": [{"id": category.category_id, "name": category.name} for category in self.categories],
            "favorites": [{"promotion_id": fav.promotion_id, "created_at": fav.created_at.isoformat()} for fav in self.favorites]
        }

    def __repr__(self):
        return f"<Tourist {self.user_id}: {self.origin}, Birthday: {self.birthday}, Gender: {self.gender}>"
