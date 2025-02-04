from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from app.services.partner_service import PartnerService
from app.auth.auth import token_required

partner_api_blueprint = Blueprint('partner_api', __name__)
api = Api(partner_api_blueprint)

class PartnerResource(Resource):
    @token_required
    def get(self, current_user, user_id):
        partner = PartnerService.get_partner_by_user_id(user_id)
        if partner:
            return jsonify(partner.serialize())
        return {'message': 'Partner not found'}, 404

    @token_required
    def put(self, current_user, user_id):
        data = request.get_json()
        partner = PartnerService.update_partner(user_id, **data)
        if partner:
            return jsonify(partner.serialize())
        return {'message': 'Partner not found'}, 404

    @token_required
    def delete(self, current_user, user_id):
        if PartnerService.delete_partner(user_id):
            return {'message': 'Partner deleted'}, 200
        return {'message': 'Partner not found'}, 404

class PartnerListResource(Resource):
    @token_required
    def get(self, current_user):
        partners = PartnerService.get_all_partners()
        return jsonify([partner.serialize() for partner in partners])

    @token_required
    def post(self, current_user):
        data = request.get_json()
        partner = PartnerService.create_partner(**data)
        if not partner:
            return {"message": "Error creating partner"}, 400
    
        return partner.serialize(), 201

api.add_resource(PartnerResource, '/partners/<int:user_id>')
api.add_resource(PartnerListResource, '/partners')