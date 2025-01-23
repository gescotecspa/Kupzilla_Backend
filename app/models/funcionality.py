from app import db

class Functionality(db.Model):
    __tablename__ = 'functionalities'

    functionality_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    platform = db.Column(db.String(50), nullable=False)

    def serialize(self):
        return {
            "id": self.functionality_id,
            "name": self.name,
            "description": self.description,
            "platform": self.platform,
        }

    def __repr__(self):
        return f"<Functionality {self.functionality_id}: {self.name}, Platform: {self.platform}>"