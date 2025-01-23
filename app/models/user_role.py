from app import db

class UserRole(db.Model):
    __tablename__ = 'user_roles'

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), primary_key=True)

    def __repr__(self):
        return f"<UserRole {self.user_id}, {self.role_id}>"