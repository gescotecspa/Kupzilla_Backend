from app import db
from app.models import TouristRating
from app.models.status import Status
from datetime import datetime, timedelta

class TouristRatingService:
    @staticmethod
    def get_rating_by_tourist_and_branch(tourist_id, branch_id):
        return TouristRating.query.filter_by(tourist_id=tourist_id, branch_id=branch_id).first()

    @staticmethod
    def create_rating(tourist_id, branch_id, rating, comment=None, status_id=None):
        # Verificar si ya existe una valoración para el turista y la sucursal
        existing_rating = TouristRatingService.get_rating_by_tourist_and_branch(tourist_id, branch_id)
        if existing_rating:
            return None, 'Rating already exists for this branch and tourist'

        # Si no se proporciona status_id, asignamos "pending" por defecto
        if not status_id:
            status_id = Status.query.filter_by(name="pending").first().id

        # Crear la nueva valoración
        new_rating = TouristRating(tourist_id=tourist_id, branch_id=branch_id, rating=rating, comment=comment, status_id=status_id, user_id=tourist_id)
        db.session.add(new_rating)
        db.session.commit()
        return new_rating, None
    
    @staticmethod
    def update_rating(rating_id, rating=None, comment=None, status_id=None):
        existing_rating = TouristRating.query.get(rating_id)
        if existing_rating:
            # Actualizamos los valores solo si se pasan como argumentos
            if rating is not None:
                existing_rating.rating = rating
            if comment is not None:
                existing_rating.comment = comment
            if status_id is not None:
                existing_rating.status_id = status_id

            db.session.commit()
            return existing_rating
        return None

    @staticmethod
    def delete_rating(rating_id):
        existing_rating = TouristRating.query.get(rating_id)
        if existing_rating:
            deleted_status = Status.query.filter_by(name="deleted").first()
            existing_rating.status_id = deleted_status.id
            existing_rating.deleted_at = db.func.current_timestamp()

            db.session.commit()
            return existing_rating
        return None

    @staticmethod
    def get_all_ratings_for_tourist(tourist_id):
        # Buscar el estado 'deleted'
        deleted_status = Status.query.filter_by(name="deleted").first()
        rejected_status = Status.query.filter_by(name="rejected").first()
        if not deleted_status:
            return {'error': 'Deleted status not found in database'}, 500
        
        # Filtrar las valoraciones para que no incluyan 'deleted' ni 'rejected'
        ratings = TouristRating.query.filter_by(tourist_id=tourist_id).filter(
            (TouristRating.status_id != deleted_status.id) & 
        (TouristRating.status_id != rejected_status.id) | 
        (TouristRating.status_id == None)
        ).all()
    
        return ratings

    @staticmethod
    def get_average_rating_for_tourist(tourist_id):
         # Buscar el estado 'deleted'
        deleted_status = Status.query.filter_by(name="deleted").first()
        rejected_status = Status.query.filter_by(name="rejected").first()

        if not deleted_status or not rejected_status:
            return {'error': 'Deleted or Rejected status not found in database'}, 500
        
        # Filtrar las valoraciones para que no incluyan 'deleted' ni 'rejected'
        ratings = TouristRating.query.filter_by(tourist_id=tourist_id).filter(
            (TouristRating.status_id != deleted_status.id) & 
            (TouristRating.status_id != rejected_status.id) | 
            (TouristRating.status_id == None)
        ).all()

        if ratings:
            return sum(rating.rating for rating in ratings) / len(ratings)
        return 0

    @staticmethod
    def approve_rating(rating_id):
        approved_status = Status.query.filter_by(name="approved").first()
        if not approved_status:
            return None, "Approved status not found"

        rating = TouristRating.query.get(rating_id)
        if not rating:
            return None, "Rating not found"

        rating.status_id = approved_status.id
        db.session.commit()
        return rating, None
    
    @staticmethod
    def reject_rating(rating_id):
        try:
            rejected_status = Status.query.filter_by(name="rejected").first()
            if not rejected_status:
                raise ValueError("Approved status not found")

            rating = TouristRating.query.get(rating_id)
            if not rating:
                raise ValueError("Rating not found")

            rating.status_id = rejected_status.id
            db.session.commit()
            return rating
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def get_ratings_last_4_weeks():
        """
        Obtiene todas las valoraciones de los turistas de las últimas 4 semanas, asegurándose de que no tengan el estado 'deleted'.
        """
        four_weeks_ago = datetime.now() - timedelta(weeks=4)
        
        # Buscar el estado 'deleted'
        deleted_status = Status.query.filter_by(name="deleted").first()
        if not deleted_status:
            return {'error': 'Deleted status not found in database'}, 500
        
        # Filtrar las valoraciones que fueron hechas en las últimas 4 semanas y no tengan el estado 'deleted'
        ratings = TouristRating.query.filter(
            TouristRating.created_at >= four_weeks_ago,
            (TouristRating.status_id != deleted_status.id) | (TouristRating.status_id == None)
        ).all()
        
        return [rating.serialize() for rating in ratings]