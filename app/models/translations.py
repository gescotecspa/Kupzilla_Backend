from app import db

class Translations(db.Model):
    __tablename__ = 'translations'

    type = db.Column(db.Integer,primary_key=True)
    reference_id = db.Column(db.Integer,primary_key=True)
    language_code = db.Column(db.String(5),primary_key=True)
    name = db.Column(db.String(120), nullable=True)

    def serialize(self):
        return {
            "type": self.type,
            "reference_id":self.reference_id,
            "language_code":self.language_code,
            "name": self.name
        }

    def __repr__(self):
        return f"<Translations {self.name}>"