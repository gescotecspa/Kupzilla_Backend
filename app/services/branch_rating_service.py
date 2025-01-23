from app import db
from app.models import BranchRating
from app.models.user import User
from app.models.status import Status
from datetime import datetime, timedelta

class BranchRatingService:
    @staticmethod
    def get_rating_by_branch_and_tourist(branch_id, user_id):
        # Devuelve la valoración de la sucursal hecha por un turista específico
        return BranchRating.query.filter_by(branch_id=branch_id, user_id=user_id).first()

    @staticmethod
    def create_rating(branch_id, user_id, rating, comment=None):
        # Crea una nueva valoración para una sucursal por un turista
        existing_rating = BranchRatingService.get_rating_by_branch_and_tourist(branch_id, user_id)
        if existing_rating:
            return None  # Ya existe una valoración para esta combinación
        
        pending_status = Status.query.filter_by(name="pending").first()
        if not pending_status:
            raise ValueError("El estado 'Pending' no existe en la tabla statuses.")

        new_rating = BranchRating(branch_id=branch_id, user_id=user_id, rating=rating, comment=comment, status_id=pending_status.id)
        db.session.add(new_rating)
        db.session.commit()
        return new_rating

    @staticmethod
    def update_rating(rating_id, rating, comment, status_id=None):
        try:
            # Busca la calificación por su ID
            rating_record = BranchRating.query.get(rating_id)
            if rating_record:
                rating_record.rating = rating
                rating_record.comment = comment
                
                if status_id:
                    status = Status.query.get(status_id)
                    if not status:
                        raise ValueError(f"El estado con ID {status_id} no existe.")
                    rating_record.status_id = status_id
                    
                db.session.commit()
                return rating_record
            return None
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def delete_rating(rating_id):
        try:
            # Busca y elimina la calificación por su ID
            rating_record = BranchRating.query.get(rating_id)
            if rating_record:
                db.session.delete(rating_record)
                db.session.commit()
                return rating_record
            return None
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def soft_delete_rating(rating_id):
        try:
            # Realiza un borrado lógico, actualizando el campo `deleted_at` y el estado a 'Deleted'
            rating_record = BranchRating.query.get(rating_id)
            if rating_record:
                deleted_status = Status.query.filter_by(name="deleted").first()
                if not deleted_status:
                    raise ValueError("El estado 'Deleted' no existe en la tabla statuses.")
                rating_record.status_id = deleted_status.id 
                rating_record.deleted_at = db.func.current_timestamp()
                db.session.commit()
                return rating_record
            return None
        except Exception as e:
            db.session.rollback()
            raise e
            
    @staticmethod
    def get_all_ratings_for_branch(branch_id):
    # Filtra las valoraciones de la sucursal, excluyendo las que tienen el estado 'deleted'
        deleted_status = Status.query.filter_by(name="deleted").first()
        rejected_status = Status.query.filter_by(name="rejected").first()
        return db.session.query(BranchRating, User.first_name).join(
            User, BranchRating.user_id == User.user_id
        ).filter(
            BranchRating.branch_id == branch_id,
            (BranchRating.status_id != deleted_status.id) & 
            (BranchRating.status_id != rejected_status.id) | 
            (BranchRating.status_id == None)
        ).all()
    @staticmethod
    def get_all_ratings_for_branch_include_rejected(branch_id):
    # Filtra las valoraciones de la sucursal, excluyendo las que tienen el estado 'deleted'
        deleted_status = Status.query.filter_by(name="deleted").first()
        return db.session.query(BranchRating, User.first_name).join(
            User, BranchRating.user_id == User.user_id
        ).filter(
            BranchRating.branch_id == branch_id,
            (BranchRating.status_id != deleted_status.id)| 
            (BranchRating.status_id == None)
        ).all()
    @staticmethod
    # Filtra las valoraciones de la sucursal que estén en estado 'pending' o 'approved'
    def get_average_rating_for_branch(branch_id):
        # Filtrar las valoraciones en los estados 'pending', 'approved' o con estado NULL
        pending_status_id = Status.query.filter_by(name="pending").first().id
        approved_status_id = Status.query.filter_by(name="approved").first().id

        ratings = BranchRating.query.filter(
            BranchRating.branch_id == branch_id,
            BranchRating.status_id.in_([pending_status_id, approved_status_id]) | (BranchRating.status_id == None),
            BranchRating.rating != None
        ).all()

        if not ratings:
            return 0

        total_rating = sum(rating.rating for rating in ratings if rating.rating is not None)
        return total_rating / len(ratings)

    @staticmethod
    def approve_rating(rating_id):
        try:
            approved_status = Status.query.filter_by(name="approved").first()
            if not approved_status:
                raise ValueError("Approved status not found")

            rating = BranchRating.query.get(rating_id)
            if not rating:
                raise ValueError("Rating not found")

            rating.status_id = approved_status.id
            db.session.commit()
            return rating
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def reject_rating(rating_id):
        try:
            rejected_status = Status.query.filter_by(name="rejected").first()
            if not rejected_status:
                raise ValueError("Approved status not found")

            rating = BranchRating.query.get(rating_id)
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
        Obtiene todas las valoraciones de las últimas 4 semanas, asegurándose de que no tengan el estado 'deleted'.
        """
        four_weeks_ago = datetime.now() - timedelta(weeks=4)
        
        # Buscar el estado 'deleted'
        deleted_status = Status.query.filter_by(name="deleted").first()
        if not deleted_status:
            return {'error': 'Deleted status not found in database'}, 500
        
        # Filtrar las valoraciones que fueron hechas en las últimas 4 semanas y no tengan el estado 'deleted'
        ratings = BranchRating.query.filter(
            BranchRating.created_at >= four_weeks_ago,
            (BranchRating.status_id != deleted_status.id) | (BranchRating.status_id == None)
        ).all()
        
        return [rating.serialize() for rating in ratings]