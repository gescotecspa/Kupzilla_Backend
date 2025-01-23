from app.models import db, Favorite

class FavoriteService:
    @staticmethod
    def add_favorite(user_id, promotion_id):
        existing_favorite = Favorite.query.filter_by(user_id=user_id, promotion_id=promotion_id).first()
        if existing_favorite:
            return None
        favorite = Favorite(user_id=user_id, promotion_id=promotion_id)
        db.session.add(favorite)
        db.session.commit()
        return favorite


    @staticmethod
    def remove_favorite(user_id, promotion_id):
        favorite = Favorite.query.filter_by(user_id=user_id, promotion_id=promotion_id).first()
        if favorite:
            db.session.delete(favorite)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_favorites_by_tourist(user_id):
        return Favorite.query.filter_by(user_id=user_id).all()

    @staticmethod
    def get_favorites_by_promotion(promotion_id):
        return Favorite.query.filter_by(promotion_id=promotion_id).all()