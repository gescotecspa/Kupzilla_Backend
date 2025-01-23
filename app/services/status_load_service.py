from app import db
from app.models.status import Status

class StatusLoadService:

    @staticmethod
    def load_statuses():
        # Lista de estados predeterminados
        predefined_statuses = ['active', 'inactive', 'suspended', 'deleted', 'pending', 'approved', 'rejected', 'edited', 'archived']

        # Consultar los estados ya existentes en la base de datos
        existing_statuses = {status.name for status in Status.query.all()}

        # Determinar los estados faltantes
        missing_statuses = set(predefined_statuses) - existing_statuses

        if not missing_statuses:
            print("Todos los estados ya están cargados en la base de datos.")
            return

        # Agregar los estados faltantes
        for status in missing_statuses:
            new_status = Status(name=status)
            db.session.add(new_status)

        db.session.commit()
        print(f"Estados cargados exitosamente en la base de datos: {', '.join(missing_statuses)}")
