from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from app.services.ContactContent_service import ContactContentService

contact_content_api_blueprint = Blueprint('contact_content_api', __name__)
api = Api(contact_content_api_blueprint)

class ContactContentResource(Resource):
    def get(self, content_id):
        content = ContactContentService.get_content_by_id(content_id)
        if content:
            return jsonify(content.serialize())
        return {'message': 'Content not found'}, 404

    def put(self, content_id):
        data = request.get_json()
        content = ContactContentService.update_content(content_id, data['language'], data['html_content'])
        if content:
            return jsonify(content.serialize())
        return {'message': 'Content not found or update failed'}, 404

    def delete(self, content_id):
        if ContactContentService.delete_content(content_id):
            return {'message': 'Content deleted'}, 200
        return {'message': 'Content not found'}, 404

class ContactContentListResource(Resource):
    def get(self):
        contents = ContactContentService.get_all_contents()
        return jsonify([content.serialize() for content in contents])

    def post(self):
        data = request.get_json()
        content = ContactContentService.create_content(data['language'], data['html_content'])
        return jsonify(content.serialize())

class ContactContentByLanguageResource(Resource):
    def get(self, language):
        content = ContactContentService.get_content_by_language(language)
        if content:
            return jsonify(content.serialize())
        return {'message': 'Content not found for this language'}, 404

# Rutas
api.add_resource(ContactContentResource, '/contact-contents/<int:content_id>')
api.add_resource(ContactContentListResource, '/contact-contents')
api.add_resource(ContactContentByLanguageResource, '/contact-contents/lang/<string:language>')
