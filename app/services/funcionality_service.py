from app.models import Functionality
from app import db

class FunctionalityService:
    @staticmethod
    def get_functionality_by_id(functionality_id):
        return Functionality.query.get(functionality_id)

    @staticmethod
    def create_functionality(name, description=None, platform=None):
        new_functionality = Functionality(name=name, description=description, platform=platform)
        db.session.add(new_functionality)
        db.session.commit()
        return new_functionality

    @staticmethod
    def update_functionality(functionality_id, name=None, description=None, platform=None):
        functionality = FunctionalityService.get_functionality_by_id(functionality_id)
        if functionality:
            if name:
                functionality.name = name
            if description is not None:
                functionality.description = description
            if platform:
                functionality.platform = platform
            db.session.commit()
        return functionality

    @staticmethod
    def delete_functionality(functionality_id):
        functionality = FunctionalityService.get_functionality_by_id(functionality_id)
        if functionality:
            db.session.delete(functionality)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_all_functionalities():
        return Functionality.query.all()