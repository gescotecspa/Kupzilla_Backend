from app import db

class Status(db.Model):
    __tablename__ = 'statuses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.String(250))

    def __repr__(self):
        return f"<Status(name={self.name})>"

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }