from app import db
from app.models.app_version import AppVersion
from sqlalchemy.exc import SQLAlchemyError

class AppVersionService:

    @staticmethod
    def get_version_by_id(version_id):
        try:
            version = AppVersion.query.get(version_id)
            if version:
                return version.serialize()  # Serializamos la versión
            return None
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error al obtener la versión: {e}")
            return None

    @staticmethod
    def update_version(version_id, version_number=None, platform=None, release_date=None, download_url=None, notes=None, is_active=None, is_required=None, app_type=None):
        try:
            version = AppVersion.query.get(version_id)
            if not version:
                return None

            if version_number is not None:
                version.version_number = version_number
            if platform is not None:
                version.platform = platform
            if release_date is not None:
                version.release_date = release_date
            if download_url is not None:
                version.download_url = download_url
            if notes is not None:
                version.notes = notes
            if is_active is not None:
                version.is_active = is_active
            if is_required is not None:
                version.is_required = is_required
            if app_type is not None:
                version.app_type = app_type

            db.session.commit()
            return version.serialize()  # Serializamos antes de retornar
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error al actualizar la versión: {e}")
            return None


    @staticmethod
    def delete_version(version_id):
        try:
            version = AppVersion.query.get(version_id)
            if version:
                db.session.delete(version)
                db.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error al eliminar la versión: {e}")
            return False

    @staticmethod
    def get_all_versions():
        try:
            versions = AppVersion.query.filter_by(is_active=True).all()
            return [version.serialize() for version in versions]
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error al obtener todas las versiones: {e}")
            return []

    @staticmethod
    def create_version(version_number, platform, release_date, download_url, notes, is_active, is_required, app_type):
        try:
            version = AppVersion(
                version_number=version_number,
                platform=platform,
                release_date=release_date,
                download_url=download_url,
                notes=notes,
                is_active=is_active,
                is_required=is_required,
                app_type=app_type
            )
            db.session.add(version)
            db.session.commit()
            return version.serialize()  # Serializamos antes de retornar
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error al crear la versión: {e}")
            return None

    @staticmethod
    def get_active_version(platform, app_type):
        print(f"Platform: {platform}, App Type: {app_type}")
        try:
            # Traemos la versión activa y obligatoria más reciente según la fecha de creación del registro
            version = AppVersion.query.filter_by(platform=platform,app_type=app_type, is_active=True) \
                .order_by(AppVersion.created_at.desc()).first()
            if version:
                return version.serialize()
            return None
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error al obtener la versión activa para {platform}: {e}")
            return None
