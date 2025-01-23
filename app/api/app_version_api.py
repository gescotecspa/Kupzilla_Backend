from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from app.services.app_version_service import AppVersionService

app_version_api_blueprint = Blueprint('app_version_api', __name__)
api = Api(app_version_api_blueprint)

class AppVersionResource(Resource):
    def get(self, version_id):
        version = AppVersionService.get_version_by_id(version_id)
        if version:
            return jsonify(version)  # Ya debe ser un diccionario serializado
        return {'message': 'Version not found'}, 404

    def put(self, version_id):
        data = request.get_json()
        version = AppVersionService.update_version(version_id, **data)
        if version:
            return jsonify(version)  # Ya debe ser un diccionario serializado
        return {'message': 'Version not found'}, 404

    def delete(self, version_id):
        if AppVersionService.delete_version(version_id):
            return {'message': 'Version deleted'}, 200
        return {'message': 'Version not found'}, 404


class AppVersionListResource(Resource):
    def get(self):
        versions = AppVersionService.get_all_versions()
        return jsonify(versions)  # Ya debe ser una lista de diccionarios serializados

    def post(self):
        data = request.get_json()
        version = AppVersionService.create_version(**data)
        if version:
            return jsonify(version)  # Ya debe ser un diccionario serializado
        return {'message': 'Error al crear version'}, 400


class ActiveAppVersionResource(Resource):
    def get(self, platform):
        app_type = request.args.get('app_type')
        if not app_type:
            return {'message': 'Es necesario incluir app_type'}, 400

        version = AppVersionService.get_active_version(platform, app_type)
        if version:
            return jsonify(version)  # Ya debe ser un diccionario serializado
        return {'message': f'No se encontró version activapara la plataforma {platform}'}, 404


api.add_resource(AppVersionResource, '/versions/<int:version_id>')
api.add_resource(AppVersionListResource, '/versions')
api.add_resource(ActiveAppVersionResource, '/versions/active/<string:platform>')
