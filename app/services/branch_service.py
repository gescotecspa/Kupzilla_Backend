from app import db
from app.models.branch import Branch
from app.models.status import Status
from ..common.image_manager import ImageManager
from datetime import datetime
from app.services.promotion_service import PromotionService

class BranchService:
    @staticmethod
    def get_branch_by_id(branch_id):
        return Branch.query.get(branch_id)

    @staticmethod
    def create_branch(partner_id, name, description, address, latitude, longitude, status_id, city_id, country_id, image_data=None):
        # Manejo de la imagen con ImageManager
        image_url = None
        if image_data:
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            image_manager = ImageManager()
            filename = f"branches/{partner_id}/{name.replace(' ', '_')}_image_{timestamp}.png"  # Cambiar aquí
            category = 'branches'
            image_url = image_manager.upload_image(image_data, filename, category)

        new_branch = Branch(
            partner_id=partner_id,
            name=name,
            description=description,
            address=address,
            latitude=latitude,
            longitude=longitude,
            status_id=status_id,
            image_url=image_url,
            country_id=country_id,
            city_id=city_id
        )
        db.session.add(new_branch)
        db.session.commit()
        return new_branch

    @staticmethod
    def update_branch(branch_id, partner_id=None, name=None, description=None, address=None, latitude=None, longitude=None, status_id=None, city_id=None, country_id=None, image_data=None):
        branch = BranchService.get_branch_by_id(branch_id)
        if branch:
            if partner_id is None:
                partner_id = branch.partner_id
            # Manejo de la imagen con ImageManager en la actualización
            if image_data:
                timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
                image_manager = ImageManager()
                filename = f"branches/{partner_id}/{name.replace(' ', '_')}_image_{timestamp}.png"
                category = 'branches'
                image_url = image_manager.upload_image(image_data, filename, category)
                branch.image_url = image_url,

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
            if country_id is not None: # Agregado
                branch.country_id = country_id
            if city_id is not None: # Agregado
                branch.city_id = city_id

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
