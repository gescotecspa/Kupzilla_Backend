from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from app.services.StatusService import StatusService

status_api_blueprint = Blueprint('status_api', __name__)
api = Api(status_api_blueprint)

class StatusResource(Resource):
    def get(self, status_id):
        status = StatusService.get_status_by_id(status_id)
        if status:
            return jsonify(status.serialize())
        return {'message': 'Status not found'}, 404

    def put(self, status_id):
        data = request.get_json()
        status = StatusService.update_status(status_id, data['name'])
        if status:
            return jsonify(status.serialize())
        return {'message': 'Status not found or update failed'}, 404

    def delete(self, status_id):
        if StatusService.delete_status(status_id):
            return {'message': 'Status deleted'}, 200
        return {'message': 'Status not found'}, 404

class StatusListResource(Resource):
    def get(self):
        statuses = StatusService.get_all_statuses()
        return jsonify([status.serialize() for status in statuses])

    def post(self):
        data = request.get_json()
        status = StatusService.create_status(data['name'])
        return jsonify(status.serialize())

api.add_resource(StatusResource, '/statuses/<int:status_id>')
api.add_resource(StatusListResource, '/statuses')
