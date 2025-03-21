from flask import jsonify
from app import db
from app.models.branch import Branch, BranchImage
from app.models.status import Status
from ..common.image_manager import ImageManager
from datetime import datetime
from app.services.promotion_service import PromotionService

class BranchService:
    @staticmethod
    def get_branch_by_id(branch_id):
        return Branch.query.get(branch_id)

    @staticmethod
    def create_branch(partner_id, name, description, address, latitude, longitude, status_id, city_id, country_id, image_data=None, images=None):
        # Crear la sucursal
        new_branch = Branch(
            partner_id=partner_id,
            name=name,
            description=description,
            address=address,
            latitude=latitude,
            longitude=longitude,
            status_id=status_id,
            country_id=country_id,
            city_id=city_id
        )
        db.session.add(new_branch)
        db.session.commit()  # Guardar la sucursal para obtener el branch_id

        # Subir la imagen principal, si existe
        if image_data:
            image_manager = ImageManager()
            # Generar un nombre único para la imagen principal
            filename = f"branches/{new_branch.branch_id}/{image_data['filename']}"
            category = 'branches'
            image_url = image_manager.upload_image(image_data['data'], filename, category)

            # Asignar la imagen principal a la sucursal
            new_image = BranchImage(branch_id=new_branch.branch_id, image_url=image_url, is_main=True)
            db.session.add(new_image)

        # Subir imágenes adicionales, si existen
        if images:
            image_manager = ImageManager()
            for image in images:
                # Generar un nombre único para cada imagen adicional
                filename = f"branches/{new_branch.branch_id}/{image['filename']}"
                category = 'branches'
                image_url = image_manager.upload_image(image['data'], filename, category)

                # Asignar cada imagen adicional a la sucursal
                new_image = BranchImage(branch_id=new_branch.branch_id, image_url=image_url, is_main=False)
                db.session.add(new_image)

        db.session.commit()
        return new_branch


    @staticmethod
    def update_branch(branch_id, partner_id=None, name=None, description=None, address=None, latitude=None, longitude=None, status_id=None, city_id=None, country_id=None, image_data=None, images=None):
        branch = BranchService.get_branch_by_id(branch_id)
        if branch:
            # Actualizar los campos básicos de la sucursal
            if partner_id is None:
                partner_id = branch.partner_id
            if partner_id is not None:
                branch.partner_id = partner_id
            if name:
                branch.name = name
            if description:
                branch.description = description
            if address:
                branch.address = address
            if latitude is not None:
                branch.latitude = latitude
            if longitude is not None:
                branch.longitude = longitude
            if status_id is not None:
                # Verificar si el estado cambió
                if branch.status_id != status_id:
                    # Buscar los estados 'inactive' y 'active'
                    inactive_status = Status.query.filter_by(name='inactive').first()
                    active_status = Status.query.filter_by(name='active').first()
                    
                    if not inactive_status or not active_status:
                        raise ValueError("Inactive or Active status not found in the database.")

                    # Actualizar el estado de las promociones asociadas
                    promotion_ids = []
            # Filtrar las promociones asociadas según el nuevo estado deseado
                    if status_id == inactive_status.id:
                        # Cambiar a 'inactive' solo las promociones que están actualmente 'active'
                        promotion_ids = [
                            promo.promotion_id
                            for promo in branch.promotions
                            if promo.status_id == active_status.id
                        ]
                    elif status_id == active_status.id:
                        # Cambiar a 'active' solo las promociones que están actualmente 'inactive'
                        promotion_ids = [
                            promo.promotion_id
                            for promo in branch.promotions
                            if promo.status_id == inactive_status.id
                        ]
                    
                    if promotion_ids:
                        PromotionService.bulk_update_promotions_status(promotion_ids, status_id)

                    # Actualizar el estado de la sucursal
                    branch.status_id = status_id
            if country_id is not None:
                branch.country_id = country_id
            if city_id is not None:
                branch.city_id = city_id

            # Actualizar la imagen principal si se pasa
            if image_data:
                # Si image_data tiene la propiedad 'image_id', se trata de una actualización de la imagen principal
                if 'image_id' in image_data:
                    # Buscar la imagen existente por image_id
                    existing_image = BranchImage.query.filter_by(image_id=image_data['image_id'], branch_id=branch.branch_id).first()
                    
                    if existing_image:
                        # Cambiar 'is_main' de la imagen principal existente a False
                        existing_main_image = BranchImage.query.filter_by(branch_id=branch.branch_id, is_main=True).first()
                        if existing_main_image and existing_main_image.image_id != existing_image.image_id:
                            existing_main_image.is_main = False
                            db.session.add(existing_main_image)
                        # Actualizar la imagen encontrada y marcarla como 'is_main'
                        existing_image.is_main = True
                        db.session.add(existing_image)
                    else:
                        # Si no se encuentra la imagen, responder con un error o manejar según lo necesario
                        return jsonify({'error': 'Image not found'}), 404
                else:
                    # Si no tiene 'image_id', entonces significa que es una nueva imagen a agregar
                    image_manager = ImageManager()
                    filename = f"branches/{branch.branch_id}/{image_data['filename']}"
                    category = 'branches'
                    image_url = image_manager.upload_image(image_data['data'], filename, category)

                    # Primero, cambiar 'is_main' de la imagen principal existente a False
                    existing_main_image = BranchImage.query.filter_by(branch_id=branch.branch_id, is_main=True).first()
                    if existing_main_image:
                        existing_main_image.is_main = False
                        db.session.add(existing_main_image)

                    # Agregar la nueva imagen principal
                    new_image = BranchImage(branch_id=branch.branch_id, image_url=image_url, is_main=True)
                    db.session.add(new_image)

            # Agregar imágenes adicionales, si existen
            if images:
                image_manager = ImageManager()
                for image in images:
                    # Generar un nombre único para cada imagen adicional
                    filename = f"branches/{branch.branch_id}/{image['filename']}"
                    category = 'branches'
                    image_url = image_manager.upload_image(image['data'], filename, category)

                    # Asignar cada imagen adicional a la sucursal
                    new_image = BranchImage(branch_id=branch.branch_id, image_url=image_url, is_main=False)
                    db.session.add(new_image)

            # Solo realizar el commit una vez después de todos los cambios
            db.session.commit()

        return branch


    @staticmethod
    def delete_branch(branch_id):
        branch = BranchService.get_branch_by_id(branch_id)
        if branch:
            db.session.delete(branch)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_all_branches():
        return (
            Branch.query.join(Status)
            .filter(Status.name == 'active')
            .order_by(Branch.name.asc())
            .all()
        )
    @staticmethod
    def get_branches_by_partner_id(partner_id):
        return (
        Branch.query.join(Status)
        .filter(
            Branch.partner_id == partner_id,
            Status.name != 'deleted'
        )
        .order_by(Branch.name.asc())
        .all()
    )
        
    @staticmethod
    def get_active_branches_by_country(country_id):
        return (
        Branch.query.join(Status)
        .filter(
            Branch.country_id == country_id,
            Status.name == 'active'
        )
        .order_by(Branch.name.asc())
        .all()
    )
        
    @staticmethod
    def delete_branch_images(image_ids):
        images = BranchImage.query.filter(BranchImage.image_id.in_(image_ids)).all()
        
        if images:
            image_manager = ImageManager()
            
            for image in images:
                try:
                    filename = image.image_url 
                    relative_path = filename.split('/upload_image/')[1] 

                    category = relative_path.split('/')[0]  
                    file_path = relative_path.split(f"{category}/")[1]  
                    print("categoria y nombre del archivo...",category, file_path)
                    image_manager.delete_image(file_path, category)  
                except Exception as e:
                    print(f"Error al eliminar la imagen {filename} del sistema: {e}")
                
                db.session.delete(image)  

            db.session.commit()
            return True 

        return False