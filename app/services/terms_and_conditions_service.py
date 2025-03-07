from app import db
from app.models.terms_and_conditions import TermsAndConditions
from datetime import datetime
from app.models.user import User
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

class TermsAndConditionsService:

    @staticmethod
    def get_latest_version():
        return TermsAndConditions.query.order_by(TermsAndConditions.created_at.desc()).first()
    
    def get_latest_version(language_code=None):
        #buscamos el termino con su idioma correspondiente 
        sql = text("SELECT * FROM terms_get_latest_by_language(:p_language_code)")
        latest_terms = db.session.execute(sql, {"p_language_code": language_code}).fetchone()

        if latest_terms:
            return TermsAndConditions(
                id=latest_terms[0],
                version = latest_terms[1], 
                created_at=latest_terms[2],
                content=latest_terms[3]
            )
        return None

    @staticmethod
    def get_all_terms():
        return TermsAndConditions.query.all()

    @staticmethod
    def get_terms_by_id(terms_id):
        return TermsAndConditions.query.get(terms_id)

    @staticmethod
    def create_terms(content, version):
        # Verificar si la versión ya existe
        existing_terms = TermsAndConditions.query.filter_by(version=version).first()
        if existing_terms:
            raise ValueError(f"Terms and conditions with version {version} already exist.")
        
        # Crear nuevos términos
        new_terms = TermsAndConditions(content=content, version=version)
        db.session.add(new_terms)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ValueError(f"Failed to create terms and conditions. Version {version} already exists.")
        return new_terms

    @staticmethod
    def update_terms(terms_id, content, version):
        terms = TermsAndConditions.query.get(terms_id)
        if terms:
            # Verificar si la versión ya está en uso por otro registro
            existing_terms = TermsAndConditions.query.filter(
                TermsAndConditions.version == version,
                TermsAndConditions.id != terms_id
            ).first()
            if existing_terms:
                raise ValueError(f"Another record with version {version} already exists.")

            terms.content = content
            terms.version = version
            db.session.commit()
            return terms
        return None

    @staticmethod
    def delete_terms(terms_id):
        terms = TermsAndConditions.query.get(terms_id)
        if terms:
            db.session.delete(terms)
            db.session.commit()
            return True
        return False

    @staticmethod
    def accept_terms(user_id):
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found.")
        
        latest_terms = TermsAndConditionsService.get_latest_version()
        if not latest_terms:
            raise ValueError("No terms available.")
        
        user.terms_id = latest_terms.id
        user.terms_accepted_at = datetime.utcnow()
        db.session.commit()
        return user
