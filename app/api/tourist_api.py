from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from app.services.tourist_service import TouristService
from app.auth.auth import token_required

tourist_api_blueprint = Blueprint('tourist_api', __name__)
api = Api(tourist_api_blueprint)

class TouristResource(Resource):
    @token_required
    def get(self, current_user, user_id):
        tourist = TouristService.get_tourist_by_user_id(user_id)
        if tourist:
            return jsonify(tourist.serialize())
        return {'message': 'Tourist not found'}, 404

    @token_required
    def put(self, current_user, user_id):
        data = request.get_json()
        tourist = TouristService.update_tourist(user_id, **data)
        if tourist:
            return jsonify(tourist.serialize())
        return {'message': 'Tourist not found'}, 404

    @token_required
    def delete(self, current_user, user_id):
        if TouristService.delete_tourist(user_id):
            return {'message': 'Tourist deleted'}, 200
        return {'message': 'Tourist not found'}, 404

class TouristListResource(Resource):
    @token_required
    def get(self, current_user):
        tourists = TouristService.get_all_tourists()
        return jsonify([tourist.serialize() for tourist in tourists])


    def post(self):
        data = request.get_json()
        tourist = TouristService.create_tourist(**data)
        return jsonify(tourist.serialize())

api.add_resource(TouristResource, '/tourists/<int:user_id>')
api.add_resource(TouristListResource, '/tourists')