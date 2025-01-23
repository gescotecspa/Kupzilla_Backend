from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from app.services.promotion_consumed_service import PromotionConsumedService
from app.auth.auth import token_required

promotion_consumed_api_blueprint = Blueprint('promotion_consumed_api', __name__)
api = Api(promotion_consumed_api_blueprint)

class PromotionConsumedResource(Resource):
    @token_required
    def get(self, current_user, id):
        promotion_consumed = PromotionConsumedService.get_promotion_consumed_by_id(id)
        if promotion_consumed:
            return jsonify(promotion_consumed.serialize())
        return {'message': 'PromotionConsumed not found'}, 404

    @token_required
    def put(self, current_user, id):
        data = request.get_json()
        try:
            # Intentar actualizar la promoción consumida
            promotion_consumed = PromotionConsumedService.update_promotion_consumed(id, data)
            if promotion_consumed:
                return jsonify(promotion_consumed.serialize())
            # Si no se encontró la promoción o falló la actualización
            return {'message': 'PromotionConsumed not found or update failed'}, 404
        except ValueError as e:
            # Si ocurre un error como que `available_quantity` quede en negativo
            response = jsonify({"error": str(e)})
            response.status_code = 400
            return response
        except Exception as e:
            # Manejar cualquier otro error
            response = jsonify({"error": "Internal server error", "details": str(e)})
            response.status_code = 500
            return response

    @token_required
    def delete(self, current_user, id):
        if PromotionConsumedService.delete_promotion_consumed(id):
            return {'message': 'PromotionConsumed deleted'}, 200
        return {'message': 'PromotionConsumed not found'}, 404

class PromotionConsumedListResource(Resource):
    @token_required
    def get(self, current_user):
        promotion_consumeds = PromotionConsumedService.get_all_promotion_consumeds()
        return jsonify([pc.serialize() for pc in promotion_consumeds])

    @token_required 
    def post(self, current_user):
        data = request.get_json()
        try:
            promotion_consumed = PromotionConsumedService.create_promotion_consumed(data)
            return jsonify(promotion_consumed.serialize())
        except ValueError as e:
            # Si ocurre un error de cantidad de promociones disponibles, devuelve un error 400
            response = jsonify({"error": str(e)})
            response.status_code = 400
            return response
        except Exception as e:
            # Manejar cualquier otro error
            response = jsonify({"error": "Error interno del servidor", "details": str(e)})
            response.status_code = 500
            return response
        
class PromotionConsumedByPartnerResource(Resource):
    @token_required
    def get(self, current_user, partner_id):
        # Obtén las promociones consumidas filtradas por partner_id
        promotions_consumed = PromotionConsumedService.get_promotion_consumeds_by_partner(partner_id)

        # Devuelve las promociones consumidas serializadas
        return jsonify([pc.serialize() for pc in promotions_consumed])

api.add_resource(PromotionConsumedResource, '/promotion_consumeds/<int:id>')
api.add_resource(PromotionConsumedListResource, '/promotion_consumeds')
api.add_resource(PromotionConsumedByPartnerResource, '/promotion_consumeds/partner/<int:partner_id>')
