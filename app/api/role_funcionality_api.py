from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from app.services.role_funcionality_service import RoleFunctionalityService

role_functionality_api_blueprint = Blueprint('role_functionality_api', __name__)
api = Api(role_functionality_api_blueprint)

class RoleFunctionalityResource(Resource):
    def post(self):
        data = request.get_json()
        role_id = data.get('role_id')
        functionality_id = data.get('functionality_id')
        if role_id is None or functionality_id is None:
            return {'message': 'Missing role_id or functionality_id'}, 400

        result = RoleFunctionalityService.add_functionality_to_role(role_id, functionality_id)
        if result:
            return {'message': 'Functionality assigned to role successfully'}, 201
        else:
            return {'message': 'Failed to assign functionality'}, 400

api.add_resource(RoleFunctionalityResource, '/assign_functionality_to_role')