from app import db
from app.models.role import Role

class RoleLoadService:

    @staticmethod
    def load_roles():
        # Lista de roles predeterminados
        predefined_roles = ['admin', 'tourist', 'associated', 'guest']

        # Consultar los roles ya existentes en la base de datos
        existing_roles = {role.role_name for role in Role.query.all()}

        # Determinar los roles faltantes
        missing_roles = set(predefined_roles) - existing_roles

        if not missing_roles:
            print("Todos los roles ya están cargados en la base de datos.")
            return

        # Agregar los roles faltantes
        for role_name in missing_roles:
            new_role = Role(role_name=role_name)
            db.session.add(new_role)

        db.session.commit()
        print(f"Roles cargados exitosamente en la base de datos: {', '.join(missing_roles)}")
