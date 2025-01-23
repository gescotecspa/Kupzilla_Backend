from app import db
from app.models.promotion import Promotion, PromotionImage
from app.models.category import Category
from app.common.image_manager import ImageManager
from app.models import Promotion, Branch, Status 
from config import Config
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import joinedload
from time import sleep

class PromotionService:
    @staticmethod
    def get_promotion_by_id(promotion_id):
        return Promotion.query.get(promotion_id)

    @staticmethod
    def create_promotion(branch_id, title, description, start_date, expiration_date, discount_percentage, available_quantity=None, partner_id=None, category_ids=[], images=[], status_id=None):
        # Crear la nueva promoción sin código QR
        new_promotion = Promotion(
            branch_id=branch_id,
            title=title,
            description=description,
            start_date=start_date,
            expiration_date=expiration_date,
            discount_percentage=discount_percentage,
            available_quantity=available_quantity,
            partner_id=partner_id,
            status_id=status_id if status_id is not None else 1,
            qr_code="" 
        )
        db.session.add(new_promotion)
        db.session.commit()  # Guardar para obtener el ID

        # Generar el código QR con el ID de la promoción y el título
        qr_code = f"{new_promotion.promotion_id}-{title.replace(' ', '_')}"

        # Actualizar la promoción con el código QR
        new_promotion.qr_code = qr_code
        db.session.commit()

        # Añadir categorías a la promoción
        for category_id in category_ids:
            category = Category.query.get(category_id)
            if category:
                new_promotion.categories.append(category)

        # Inicializar ImageManager para manejar las imágenes
        image_manager = ImageManager()

        # Procesar y subir cada imagen
        for image_data in images:
            # Generar un nombre de archivo único para cada imagen
            
            filename = f"promotions/{new_promotion.promotion_id}/{image_data['filename']}"
            
            # Subir la imagen y obtener la URL pública
            category='promotions'
            
            image_url = image_manager.upload_image(image_data['data'], filename, category)
            # Crear una instancia de PromotionImage y asociarla a la promoción
            new_image = PromotionImage(promotion=new_promotion, image_path=image_url)
            db.session.add(new_image)
        
        # Guardar todos los cambios en la base de datos
        db.session.commit()
        
        return new_promotion

    @staticmethod
    def update_promotion(promotion_id, title=None, description=None, start_date=None, expiration_date=None, qr_code=None, discount_percentage=None, available_quantity=None, partner_id=None, branch_id=None, category_ids=None, images=None, status_id=None):
        # Obtener la promoción existente
        promotion = PromotionService.get_promotion_by_id(promotion_id)
        if promotion:
            # Actualizar los campos de la promoción si se proporcionan nuevos valores
            if title:
                promotion.title = title
            if description:
                promotion.description = description
            if start_date:
                promotion.start_date = start_date
            if expiration_date:
                promotion.expiration_date = expiration_date
            if qr_code:
                promotion.qr_code = qr_code
            if discount_percentage is not None:
                promotion.discount_percentage = discount_percentage
            if available_quantity is not None:
                promotion.available_quantity = available_quantity
            if partner_id is not None:
                promotion.partner_id = partner_id
            if branch_id is not None:
                promotion.branch_id = branch_id
            if status_id is not None:
                promotion.status_id = status_id
            
            # Actualizar las categorías si se proporcionan nuevas
            if category_ids is not None:
                promotion.categories.clear()
                for category_id in category_ids:
                    category = Category.query.get(category_id)
                    if category:
                        promotion.categories.append(category)

            # Actualizar las imágenes si se proporcionan nuevas
            if images is not None:
                
                # Inicializar ImageManager para manejar las nuevas imágenes
                image_manager = ImageManager()

                # Procesar y subir cada nueva imagen
                for image_data in images:
                    filename = f"promotions/{promotion.promotion_id}/{image_data['filename']}"
                    category='promotions'
                    image_url = image_manager.upload_image(image_data['data'], filename, category)
                    new_image = PromotionImage(promotion_id=promotion_id, image_path=image_url)
                    db.session.add(new_image)
            
            # Guardar todos los cambios en la base de datos
            db.session.commit()

        return promotion

    @staticmethod
    def delete_promotion(promotion_id):
        # Obtener la promoción existente
        promotion = PromotionService.get_promotion_by_id(promotion_id)
        if promotion:
            # Eliminar todas las imágenes asociadas
            images = PromotionImage.query.filter(PromotionImage.promotion_id == promotion_id).all()
            for image in images:
                db.session.delete(image)

            # Eliminar la promoción
            db.session.delete(promotion)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_all_promotions(retries=2, delay=3):
        attempt = 0
        while attempt < retries:
            try:
                # Filtrar promociones donde el estado no sea "deleted"
                return (
                    Promotion.query.join(Status)
                    .filter(Status.name != 'deleted')
                    .options(joinedload(Promotion.status))  # Pre-carga la relación status
                    .all()
                )
            except OperationalError as e:
                attempt += 1
                print(f"Error de conexión: {e}. Reintentando {attempt}/{retries}...")
                sleep(delay)  # Esperar antes de reintentar
        # Lanzar excepción si después de varios intentos no se logra
        raise OperationalError(f"Fallo después de {retries} intentos")
    
    @staticmethod
    def get_active_promotions(retries=2, delay=3):
        attempt = 0
        while attempt < retries:
            try:
                return (
                    Promotion.query.join(Status)
                    .filter(Status.name == 'active')
                    .options(joinedload(Promotion.status))
                    .all()
                )
            except OperationalError as e:
                attempt += 1
                print(f"Error de conexión: {e}. Reintentando {attempt}/{retries}...")
                sleep(delay)
        raise OperationalError(f"Fallo después de {retries} intentos")
    
    @staticmethod
    def delete_promotion_images(image_ids):
        images = PromotionImage.query.filter(PromotionImage.image_id.in_(image_ids)).all()
        if images:
            image_manager = ImageManager()
            for image in images:
                try:
                    filename = image.image_path

                   
                    relative_path = filename.split('/upload_image/')[1]

                    category = relative_path.split('/')[0]
                    file_path = relative_path.split(f"{category}/")[1]

                    image_manager.delete_image(file_path, category)
                except Exception as e:
                    print(f"Error al eliminar la imagen {filename} del sistema: {e}")
                db.session.delete(image)

            db.session.commit()
            return True
        return False

    @staticmethod
    def get_promotions_by_partner(partner_id):
        return (
        Promotion.query
        .join(Branch)
        .join(Status, Promotion.status_id == Status.id)
        .filter(
            Branch.partner_id == partner_id,
            Status.name != 'deleted' 
        )
        .all()
    )
    
    @staticmethod
    def bulk_update_promotions_status(promotion_ids, status_id):
        try:
            promotions = Promotion.query.filter(Promotion.promotion_id.in_(promotion_ids)).all()
            
            if not promotions:
                return None

            for promotion in promotions:
                promotion.status_id = status_id

            db.session.commit()
            return promotions

        except Exception as e:
            print(f"Error al actualizar promociones: {e}")
            db.session.rollback()
            return None
    #eliminar imagenes google storage
    # @staticmethod
    # def delete_promotion_images(image_ids):
    #     images = PromotionImage.query.filter(PromotionImage.image_id.in_(image_ids)).all()
    #     if images:
    #         image_manager = ImageManager()
    #         for image in images:
    #             # Intentar borrar la imagen del sistema de almacenamiento
    #             try:
    #                 filename = image.image_path
    #                 relative_path = filename.split(f"{Config.GCS_BUCKET_NAME}/")[1]

    #                 # Determinar la categoría a partir de la ruta del archivo
    #                 category = relative_path.split('/')[0] 
    #                 file_path = relative_path.split(f"{category}/")[1] 

    #                 # Llamar a la función delete_image con el nombre de archivo y categoría
    #                 image_manager.delete_image(file_path, category)
    #             except Exception as e:
    #                 print(f"Error al eliminar la imagen {filename} del sistema: {e}")
    #             db.session.delete(image)
            
    #         # Guardar los cambios en la base de datos
    #         db.session.commit()
    #         return True
    #     return False