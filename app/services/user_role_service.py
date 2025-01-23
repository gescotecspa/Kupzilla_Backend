from app import db
from app.models import UserRole, User, Role

class UserRoleService:
    @staticmethod
    def add_role_to_user(user_id, role_id):
        user = User.query.get(user_id)
        role = Role.query.get(role_id)
        if user and role:
            user_role = UserRole(user_id=user_id, role_id=role_id)
            db.session.add(user_role)
            db.session.commit()
            return user_role
        return None

    @staticmethod
    def remove_role_from_user(user_id, role_id):
        user_role = UserRole.query.filter_by(user_id=user_id, role_id=role_id).first()
        if user_role:
            db.session.delete(user_role)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_roles_for_user(user_id):
        return UserRole.query.filter_by(user_id=user_id).all()

    @staticmethod
    def get_users_for_role(role_id):
        return UserRole.query.filter_by(role_id=role_id).all()
    
    @staticmethod
    def clear_roles_for_user(user_id):
        db.session.query(UserRole).filter_by(user_id=user_id).delete()
        db.session.commit()