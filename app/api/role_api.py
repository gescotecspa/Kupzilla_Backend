from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from app.services.role_service import RoleService

role_api_blueprint = Blueprint('role_api', __name__)
api = Api(role_api_blueprint)

class RoleResource(Resource):
    def get(self, role_id):
        role = RoleService.get_role_by_id(role_id)
        if role:
            return jsonify(role.serialize())
        return {'message': 'Role not found'}, 404

    def put(self, role_id):
        data = request.get_json()
        role = RoleService.update_role(role_id, data['role_name'])
        if role:
            return jsonify(role.serialize())
        return {'message': 'Role not found or update failed'}, 404

    def delete(self, role_id):
        if RoleService.delete_role(role_id):
            return {'message': 'Role deleted'}, 200
        return {'message': 'Role not found'}, 404

class RoleListResource(Resource):
    def get(self):
        roles = RoleService.get_all_roles()
        return jsonify([role.serialize() for role in roles])

    def post(self):
        data = request.get_json()
        role = RoleService.create_role(data['role_name'])
        return jsonify(role.serialize())

api.add_resource(RoleResource, '/roles/<int:role_id>')
api.add_resource(RoleListResource, '/roles')