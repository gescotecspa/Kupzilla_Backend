from app import db
from app.models import RoleFunctionality, Role, Functionality

class RoleFunctionalityService:
    @staticmethod
    def add_functionality_to_role(role_id, functionality_id):
        role = Role.query.get(role_id)
        functionality = Functionality.query.get(functionality_id)
        if role and functionality:
            role_functionality = RoleFunctionality(role_id=role_id, functionality_id=functionality_id)
            db.session.add(role_functionality)
            db.session.commit()
            return role_functionality
        return None

    @staticmethod
    def remove_functionality_from_role(role_id, functionality_id):
        role_functionality = RoleFunctionality.query.filter_by(role_id=role_id, functionality_id=functionality_id).first()
        if role_functionality:
            db.session.delete(role_functionality)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_functionalities_for_role(role_id):
        return RoleFunctionality.query.filter_by(role_id=role_id).all()

    @staticmethod
    def get_roles_for_functionality(functionality_id):
        return RoleFunctionality.query.filter_by(functionality_id=functionality_id).all()