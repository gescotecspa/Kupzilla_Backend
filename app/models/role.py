from app import db

class Role(db.Model):
    __tablename__ = 'roles'
    
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(255), nullable=False)

    # Relación con functionalities
    functionalities = db.relationship('Functionality', secondary='role_functionalities', backref=db.backref('roles', lazy='dynamic'))

    def serialize(self):
        return {
            "role_id": self.role_id,
            "role_name": self.role_name,
            "functionalities": [functionality.serialize() for functionality in self.functionalities]
        }