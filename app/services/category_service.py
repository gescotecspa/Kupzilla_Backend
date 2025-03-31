from app.models.category import Category
from sqlalchemy.orm import aliased
from app.models.translations import Translations
from app import db

class CategoryService:
    @staticmethod
    def get_category_by_id(category_id):
        return Category.query.get(category_id)

    @staticmethod
    def get_all_categories():
        return Category.query.order_by(Category.name.asc()).all()

    @staticmethod
    def create_category(name):
        new_category = Category(name=name)
        db.session.add(new_category)
        db.session.commit()
        return new_category

    @staticmethod
    def update_category(category_id, name):
        category = CategoryService.get_category_by_id(category_id)
        if category:
            category.name = name
            db.session.commit()
            return category
        return None

    @staticmethod
    def delete_category(category_id):
        category = CategoryService.get_category_by_id(category_id)
        if category:
            db.session.delete(category)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_by_language(language_code):
        # Alias para la tabla de traducciones
        TranslationAlias = aliased(Translations)

        # Realizar el JOIN condicional
        categories = (
            db.session.query(Category, TranslationAlias.name)
            .outerjoin(
                TranslationAlias,
                (TranslationAlias.reference_id == Category.category_id) &
                (TranslationAlias.type == 1) &
                (TranslationAlias.language_code == language_code.lower())
            )
            .order_by(TranslationAlias.name.asc())
            .all()
        )

        # Serializar el resultado
        return [
            {
                "category_id": category.category_id,
                "name": translation if translation else category.name
            }
            for category, translation in categories
        ]
