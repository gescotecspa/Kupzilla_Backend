from app import db
from app.models import Partner, Category
from sqlalchemy.exc import IntegrityError

class PartnerService:
    @staticmethod
    def get_partner_by_user_id(user_id):
        return Partner.query.get(user_id)

    @staticmethod
    def create_partner(user_id, address, contact_info, business_type, category_ids=[]):
        new_partner = Partner(user_id=user_id, address=address, contact_info=contact_info, business_type=business_type)
        db.session.add(new_partner)
        for category_id in category_ids:
            category = Category.query.get(category_id)
            if category:
                new_partner.categories.append(category)
        db.session.commit()
        return new_partner

    @staticmethod
    def update_partner(user_id, address=None, contact_info=None, business_type=None, category_ids=None):
        partner = PartnerService.get_partner_by_user_id(user_id)
        if partner:
            if address is not None:
                partner.address = address
            if contact_info is not None:
                partner.contact_info = contact_info
            if business_type is not None:
                partner.business_type = business_type
            if category_ids is not None:
                # Limpiar las categorías existentes
                partner.categories = []
                # Agregar nuevas categorías
                for category_id in category_ids:
                    category = Category.query.get(category_id)
                    if category:
                        partner.categories.append(category)
            db.session.commit()
        return partner

    @staticmethod
    def delete_partner(user_id):
        partner = PartnerService.get_partner_by_user_id(user_id)
        if partner:
            db.session.delete(partner)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_all_partners():
        return Partner.query.all()
