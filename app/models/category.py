from app import db

class Category(db.Model):
    __tablename__ = 'categories'

    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)

    def serialize(self):
        return {
            "category_id": self.category_id,
            "name": self.name
        }

    def __repr__(self):
        return f"<Category {self.name}>"
