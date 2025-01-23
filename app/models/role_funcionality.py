from app import db

class RoleFunctionality(db.Model):
    __tablename__ = 'role_functionalities'

    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), primary_key=True)
    functionality_id = db.Column(db.Integer, db.ForeignKey('functionalities.functionality_id'), primary_key=True)

    def __repr__(self):
        return f"<RoleFunctionality {self.role_id}, {self.functionality_id}>"