from app.models.status import Status
from app import db

class StatusService:

    @staticmethod
    def get_status_by_id(status_id):
        return Status.query.get(status_id)

    @staticmethod
    def get_all_statuses():
        return Status.query.all()

    @staticmethod
    def create_status(name):
        new_status = Status(name=name)
        db.session.add(new_status)
        db.session.commit()
        return new_status

    @staticmethod
    def update_status(status_id, name):
        status = Status.query.get(status_id)
        if status:
            status.name = name
            db.session.commit()
            return status
        return None

    @staticmethod
    def delete_status(status_id):
        status = Status.query.get(status_id)
        if status:
            db.session.delete(status)
            db.session.commit()
            return True
        return False
