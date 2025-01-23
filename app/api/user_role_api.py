from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from app.services.user_role_service import UserRoleService

user_role_api_blueprint = Blueprint('user_role_api', __name__)
api = Api(user_role_api_blueprint)

class UserRoleResource(Resource):
    def post(self):
        data = request.get_json()
        user_id = data.get('user_id')
        role_ids = data.get('role_ids')

        if user_id is None or not role_ids:
            return {'message': 'Missing user_id or role_ids'}, 400

        UserRoleService.clear_roles_for_user(user_id)
        
        failed_roles = []
        for role_id in role_ids:
            result = UserRoleService.add_role_to_user(user_id, role_id)
            if not result:
                failed_roles.append(role_id)

        if failed_roles:
            return {
                'message': 'Some roles failed to assign',
                'failed_roles': failed_roles
            }, 400
        else:
            return {'message': 'Roles updated successfully'}, 201
        
class BulkUserRoleResource(Resource):
    def post(self):
        data = request.get_json()

        if not isinstance(data, list):
            return {'message': 'Input data must be a list of user-role pairs'}, 400

        failed_users = []

        for user_role in data:
            user_id = user_role.get('user_id')
            role_ids = user_role.get('role_ids')

            if user_id is None or not role_ids:
                failed_users.append({
                    'user_id': user_id,
                    'error': 'Missing user_id or role_ids'
                })
                continue

            UserRoleService.clear_roles_for_user(user_id)

            failed_roles = []
            for role_id in role_ids:
                result = UserRoleService.add_role_to_user(user_id, role_id)
                if not result:
                    failed_roles.append(role_id)

            if failed_roles:
                failed_users.append({
                    'user_id': user_id,
                    'failed_roles': failed_roles
                })

        if failed_users:
            return {
                'message': 'Some users had errors during role assignment',
                'failed_users': failed_users
            }, 400
        else:
            return {'message': 'Roles updated successfully for all users'}, 201       

api.add_resource(UserRoleResource, '/assign_roles_to_user')

api.add_resource(BulkUserRoleResource, '/assign_roles_to_multiple_users')
