from app.models.role import Role
from app import db

class RoleService:
    @staticmethod
    def get_role_by_id(role_id):
        return Role.query.get(role_id)

    @staticmethod
    def get_all_roles():
        return Role.query.all()

    @staticmethod
    def create_role(role_name):
        new_role = Role(role_name=role_name)
        db.session.add(new_role)
        db.session.commit()
        return new_role

    @staticmethod
    def update_role(role_id, role_name):
        role = RoleService.get_role_by_id(role_id)
        if role:
            role.role_name = role_name
            db.session.commit()
            return role
        else:
            return None

    @staticmethod
    def delete_role(role_id):
        role = RoleService.get_role_by_id(role_id)
        if role:
            db.session.delete(role)
            db.session.commit()
            return True
        return False