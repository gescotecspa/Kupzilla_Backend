from app import db
from app.models import Tourist, Category

class TouristService:
    @staticmethod
    def get_tourist_by_user_id(user_id):
        # Devolvemos el turista especificado por user_id
        return Tourist.query.get(user_id)

    @staticmethod
    def create_tourist(user_id, origin, birthday=None, gender=None, category_ids=[]):
        # Crea un nuevo registro de turista en la base de datos
        new_tourist = Tourist(user_id=user_id, origin=origin, birthday=birthday if birthday else None, gender=gender)
        db.session.add(new_tourist)
        
        # Asocia las categorías con el turista mediante la tabla intermedia
        for category_id in category_ids:
            category = Category.query.get(category_id)
            if category:
                new_tourist.categories.append(category)

        db.session.commit()
        return new_tourist

    @staticmethod
    def update_tourist(user_id, origin=None, birthday=None, gender=None, category_ids=None):
    # Encuentra el registro de turista basado en user_id y actualiza su información
        print(user_id)
        tourist = TouristService.get_tourist_by_user_id(user_id)
        
        if tourist:
            if origin:
                tourist.origin = origin
            if birthday:
                tourist.birthday = birthday
            if gender:
                tourist.gender = gender

            # Actualiza las categorías asociadas
            if category_ids is not None:
                # Primero limpiamos todas las relaciones existentes
                tourist.categories = []
                for category_id in category_ids:
                    category = Category.query.get(category_id)
                    if category:
                        tourist.categories.append(category)

            db.session.commit()
        return tourist

    @staticmethod
    def delete_tourist(user_id):
        # Elimina el registro del turista especificado por user_id
        tourist = TouristService.get_tourist_by_user_id(user_id)
        if tourist:
            db.session.delete(tourist)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_all_tourists():
        # Devuelve todos los registros de turistas en la base de datos
        return Tourist.query.all()