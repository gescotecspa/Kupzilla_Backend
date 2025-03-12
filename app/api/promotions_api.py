from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from app.services.promotion_service import PromotionService
from app.auth.auth import token_required

promotion_api_blueprint = Blueprint('promotion_api', __name__)
api = Api(promotion_api_blueprint)

class PromotionResource(Resource):
    @token_required
    def get(self, current_user, promotion_id):
        promotion = PromotionService.get_promotion_by_id(promotion_id)
        if promotion:
            return jsonify(promotion.serialize())
        return {'message': 'Promotion not found'}, 404

    @token_required
    def put(self, current_user, promotion_id):
        data = request.get_json()
        promotion = PromotionService.update_promotion(promotion_id, **data)
        if promotion:
            return jsonify(promotion.serialize())
        return {'message': 'Promotion not found'}, 404

    @token_required
    def delete(self, current_user, promotion_id):
        if PromotionService.delete_promotion(promotion_id):
            return {'message': 'Promotion deleted'}, 200
        return {'message': 'Promotion not found'}, 404

class PromotionListResource(Resource):
    @token_required
    def get(self, current_user):
        promotions = PromotionService.get_all_promotions()
        return jsonify([promotion.serialize() for promotion in promotions])

    @token_required
    def post(self, current_user):
        data = request.get_json()
        promotion = PromotionService.create_promotion(**data)
        return jsonify(promotion.serialize())

class PromotionImageResource(Resource):
    @token_required
    def post(self, current_user):
        data = request.get_json()
        image_ids = data.get('image_ids', [])
        print(image_ids)
        if PromotionService.delete_promotion_images(image_ids):
            return {'message': 'Images deleted'}, 200
        return {'message': 'Images not found'}, 404    

class PromotionByPartnerResource(Resource):
    @token_required
    def get(self, current_user, partner_id):
        promotions = PromotionService.get_promotions_by_partner(partner_id)
        return jsonify([promotion.serialize(include_user_info=False) for promotion in promotions])

class PromotionBulkDeleteResource(Resource):
    @token_required
    def put(self, current_user):
        data = request.get_json()
        promotion_ids = data.get('promotion_ids', [])
        status_id = data.get('status_id')  # Suponiendo que 'status_id' es el valor que indica que la promoción fue eliminada

        # Verificar si se recibió el arreglo de IDs de promociones y el status_id
        if not promotion_ids or not status_id:
            return {'message': 'Missing promotion_ids or status_id'}, 400

        # Llamamos al servicio para actualizar las promociones
        updated_promotions = PromotionService.bulk_update_promotions_status(promotion_ids, status_id)
        
        if updated_promotions:
            return {'message': 'Promotions updated successfully'}, 200
        return {'message': 'Failed to update promotions'}, 500

class ActivePromotionsResource(Resource):
    @token_required
    def get(self, current_user, version=None):
        if version == 'v2':
            # Mantener el servicio original, solo ajustando el uso para la versión 2
            promotions = PromotionService.get_active_promotions()
            return jsonify([promotion.serialize(include_user_info=False, include_branch_name=True) for promotion in promotions])
        else:
            return {'message': 'API version not supported'}, 400

# Nuevo: Versión 2 para promociones activas
class AllPromotionsResourceVersioned(Resource):
    @token_required
    def get(self, current_user, version):
        if version == 'v2':
            promotions = PromotionService.get_all_promotions()
            return jsonify([promotion.serialize(include_user_info=False, include_branch_name=True) for promotion in promotions])
        else:
            return {'message': 'API version not supported'}, 400
        
class PromotionByCityResource(Resource):
    @token_required
    def get(self, current_user, city_id=None):
        try:
            if city_id:
                # Obtener promociones activas para la ciudad específica
                promotions = PromotionService.get_active_promotions_by_city(city_id)
            else:
                # Obtener todas las promociones activas
                promotions = PromotionService.get_active_promotions()

            # Si el servicio devuelve un error o promociones vacías
            if promotions is None:
                return {'message': 'Error retrieving promotions'}, 500  # Error en el servicio
            elif isinstance(promotions, list) and not promotions:
                return jsonify([])  # Devolver un arreglo vacío si no hay promociones

            return jsonify([promotion.serialize(include_user_info=False, include_branch_name=True) for promotion in promotions])

        except Exception as e:
            return {'message': f'An error occurred: {str(e)}'}, 500 
        
class ActivePromotionsByCountryResource(Resource):
    @token_required
    def get(self, current_user, country_id):
        try:
            # Obtener promociones activas por país
            active_promotions = PromotionService.get_active_promotions_by_country(country_id)

            if active_promotions is None:
                return {'message': 'Error retrieving active promotions'}, 500  # Error en el servicio
            elif not active_promotions:
                return jsonify([])  # Devolver un arreglo vacío si no hay promociones activas

            return jsonify([promotion.serialize(include_user_info=False, include_branch_name=True) for promotion in active_promotions])

        except Exception as e:
            return {'message': f'An error occurred: {str(e)}'}, 500        

api.add_resource(PromotionResource, '/promotions/<int:promotion_id>')
api.add_resource(PromotionImageResource, '/promotion_images/delete')
api.add_resource(PromotionByPartnerResource, '/partners/<int:partner_id>/promotions')
api.add_resource(PromotionBulkDeleteResource, '/promotions/bulk_delete')
api.add_resource(PromotionListResource, '/promotions') # Ruta para promociones activas (version inicial)
api.add_resource(ActivePromotionsResource, '/<string:version>/promotions/active')  # Ruta para promociones activas (turistas)
api.add_resource(AllPromotionsResourceVersioned, '/<string:version>/promotions')  # Ruta versionada para todas las promociones sin branch details
api.add_resource(PromotionByCityResource, '/promotions/cities', '/promotions/cities/<int:city_id>')
api.add_resource(ActivePromotionsByCountryResource, '/promotions/countries/<int:country_id>')