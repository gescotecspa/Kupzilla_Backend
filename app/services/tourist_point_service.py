from app.models import TouristPoint, Image, Rating, Status
from app import db
from ..common.image_manager import ImageManager
from config import Config
from datetime import datetime, timedelta


class TouristPointService:
    @staticmethod
    def create_tourist_point(data):
        # print("data recibida al crear punto",data)
        active_status = Status.query.filter_by(name="active").first()
        if not active_status:
            print("El estado 'active' no está disponible.")
            return None
        tourist_point = TouristPoint(
            title=data['title'],
            description=data.get('description'),
            latitude=data['latitude'],
            longitude=data['longitude'],
            status_id=active_status.id
        )
        
        db.session.add(tourist_point)
        db.session.commit()
        
        # Agregar imágenes si se proporcionan
        if 'images' in data:
            image_manager = ImageManager()
            for image_data in data['images']:
                filename = f"tourist_points/{tourist_point.id}/{image_data['filename']}"
                category = 'tourist_points'
                image_url = image_manager.upload_image(image_data['data'], filename, category)
                print(image_url, tourist_point.id)
                image = Image(image_path=image_url, tourist_point_id=tourist_point.id)
                db.session.add(image)
        
        db.session.commit()
        return tourist_point

    def update_tourist_point(tourist_point_id, data):
        tourist_point = TouristPoint.query.get(tourist_point_id)
        
        if not tourist_point:
            return None
        
        # Actualizar los campos del punto turístico
        tourist_point.title = data.get('title', tourist_point.title)
        tourist_point.description = data.get('description', tourist_point.description)
        tourist_point.latitude = data.get('latitude', tourist_point.latitude)
        tourist_point.longitude = data.get('longitude', tourist_point.longitude)
            
        # Agregar nuevas imágenes
        if 'images' in data:
            image_manager = ImageManager()
            for image_data in data['images']:
                filename = f"tourist_points/{tourist_point.id}/{image_data['filename']}"
                category = 'tourist_points'
                image_url = image_manager.upload_image(image_data['data'], filename, category)
                image = Image(image_path=image_url, tourist_point_id=tourist_point_id)
                db.session.add(image)
        
        db.session.commit()
        return tourist_point.serialize()

    def get_all_tourist_points():
        active_status = Status.query.filter_by(name="active").first()
        if not active_status:
            return []

        tourist_points = (
            TouristPoint.query
            .filter_by(status_id=active_status.id)
            .order_by(TouristPoint.title.asc())
            .all()
        )
        return [tp.serialize() for tp in tourist_points]

    def get_tourist_point_by_id(tourist_point_id):
        tourist_point = TouristPoint.query.get(tourist_point_id)
        return tourist_point.serialize() if tourist_point else None

    def add_image(tourist_point_id, image_data):
        image_manager = ImageManager()
        filename = f"tourist_points/{tourist_point_id}/{image_data['filename']}"
        category = 'tourist_points'
        image_url = image_manager.upload_image(image_data['data'], filename, category)
        
        image = Image(image_path=image_url, tourist_point_id=tourist_point_id)
        db.session.add(image)
        db.session.commit()
        return image.serialize()  # Devuelve el resultado serializado

    def add_rating(tourist_point_id, tourist_id, rating, comment=None):
        pending_status = Status.query.filter_by(name="pending").first()
        # Verificar si el turista ya ha calificado este punto turístico
        existing_rating = Rating.query.filter_by(
            tourist_point_id=tourist_point_id,
            tourist_id=tourist_id
        ).first()
        
        if (existing_rating):
            return {'message': 'You have already rated this tourist point'}, 400  
        
        # Crear la nueva calificación
        new_rating = Rating(
            tourist_point_id=tourist_point_id,
            tourist_id=tourist_id,
            rating=rating,
            comment=comment,
            status_id=pending_status.id if pending_status else None,
        )
        db.session.add(new_rating)
        db.session.commit()
        
        return new_rating.serialize()

    def delete_rating(rating_id):
        rating = Rating.query.get(rating_id)
        if not rating:
            return None

        deleted_status = Status.query.filter_by(name="deleted").first()
        if not deleted_status:
            return {'error': 'Deleted status not found'}, 500

        rating.status_id = deleted_status.id
        rating.deleted_at = db.func.current_timestamp() 
        db.session.commit()

        return True

    def update_rating(rating_id, data):
        rating = Rating.query.get(rating_id)
        if not rating:
            return None

        if 'rating' in data:
            rating.rating = data['rating']
        if 'comment' in data:
            rating.comment = data['comment']
        if 'status_id' in data:
            rating.status_id = data['status_id']

        db.session.commit()
        return rating.serialize()

    def get_average_rating(tourist_point_id):
        deleted_status = Status.query.filter_by(name="deleted").first()
        rejected_status = Status.query.filter_by(name="rejected").first()

        if not deleted_status or not rejected_status:
            return {'error': 'Deleted or Rejected status not found in database'}, 500
        
        ratings = Rating.query.filter(
            Rating.tourist_point_id == tourist_point_id,
            (Rating.status_id != deleted_status.id) & 
            (Rating.status_id != rejected_status.id) | 
            (Rating.status_id == None)
        ).all()
        if not ratings:
            return 0
        avg_rating = sum(r.rating for r in ratings) / len(ratings)
        return {'average_rating': avg_rating}

    def get_ratings_by_tourist_point(tourist_point_id):
        deleted_status = Status.query.filter_by(name="deleted").first()
        rejected_status = Status.query.filter_by(name="rejected").first()

        if not deleted_status or not rejected_status:
            return {'error': 'Deleted or Rejected status not found in database'}, 500

        ratings = Rating.query.filter(
            Rating.tourist_point_id == tourist_point_id,
            (Rating.status_id != deleted_status.id) & 
            (Rating.status_id != rejected_status.id) | 
            (Rating.status_id == None)
        ).all()
        return ratings

    def delete_tourist_point_images(image_ids):
    # Obtiene las imágenes de los puntos turísticos por su ID
        images = Image.query.filter(Image.id.in_(image_ids)).all()
        
        if images:
            image_manager = ImageManager()
            for image in images:
                try:
                    filename = image.image_path  # Obtiene la ruta completa de la imagen
                    relative_path = filename.split('/upload_image/')[1]
                    category = relative_path.split('/')[0]
                    file_path = relative_path.split(f"{category}/")[1] 

                    # Elimina la imagen
                    image_manager.delete_image(file_path, category)
                except Exception as e:
                    print(f"Error al eliminar la imagen {filename} del sistema: {e}")
                
                db.session.delete(image)

            db.session.commit()
            return True

        return False  
        #Google storage
    # def delete_images(image_ids):
    #     image_manager = ImageManager()
        
    #     try:
    #         # Busca todas las imágenes por su ID
    #         images_to_delete = Image.query.filter(Image.id.in_(image_ids)).all()

    #         if not images_to_delete:
    #             return None

    #         # Elimina las imágenes del bucket y de la base de datos
    #         for image in images_to_delete:
    #             # Extrae la ruta completa desde la URL de la imagen
    #             file_path = image.image_path # Ajusta según el campo que uses en el modelo
    #             relative_path = file_path.split(f"{Config.GCS_BUCKET_NAME}/")[1]  # Obtener la ruta relativa (sin el primer "/")
    #             # print(relative_path)
    #             # file_path ahora contiene 'tourist_points/28/LOGOASOCIADOS.png', por ejemplo
    #             success = image_manager.delete_image(relative_path)  # Pasa la ruta relativa correcta
    #             if not success:
    #                 print(f"Failed to delete image: {file_path}")

    #             # Elimina la entrada en la base de datos
    #             db.session.delete(image)

    #         db.session.commit()
    #         return True
    #     except Exception as e:
    #         db.session.rollback()
    #         print(f"Error deleting images: {e}")
    #         return False

    def delete_tourist_point(tourist_point_id):
        tourist_point = TouristPoint.query.get(tourist_point_id)
        
        if not tourist_point:
            return None

        # Cambiar el estado del punto turístico a "deleted"
        deleted_status = Status.query.filter_by(name='deleted').first()
        if deleted_status:
            tourist_point.status_id = deleted_status.id
            db.session.commit()
            return tourist_point.serialize()
        
        return None    
    
    def get_all_except_deleted():
        deleted_status = Status.query.filter_by(name="deleted").first()
        
        if not deleted_status:
            tourist_points = TouristPoint.query.order_by(TouristPoint.title.asc()).all()
        else:
            tourist_points = (
                TouristPoint.query
                .filter(TouristPoint.status_id != deleted_status.id)
                .order_by(TouristPoint.title.asc())
                .all()
            )
        return [tp.serialize() for tp in tourist_points]
    
    @staticmethod
    def get_comments_last_4_weeks():
        """
        Obtiene los comentarios de los puntos turísticos de la última semana, incluyendo aquellos con estado 'deleted'.
        """
        one_week_ago = datetime.now() - timedelta(weeks=4)
        
        deleted_status = Status.query.filter_by(name="deleted").first()
        if not deleted_status:
            return {'error': 'Deleted status not found in database'}, 500
        
        comments = Rating.query.filter(
            Rating.created_at >= one_week_ago,
            (Rating.status_id != deleted_status.id) | (Rating.status_id == None)
        ).all()
        
        return [comment.serialize() for comment in comments]
    
    @staticmethod
    def approve_rating(rating_id):
        approved_status = Status.query.filter_by(name="approved").first()
        if not approved_status:
            return None, "Approved status not found"

        rating = Rating.query.get(rating_id)
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

            rating = Rating.query.get(rating_id)
            if not rating:
                raise ValueError("Rating not found")

            rating.status_id = rejected_status.id
            db.session.commit()
            return rating
        except Exception as e:
            db.session.rollback()
            raise e