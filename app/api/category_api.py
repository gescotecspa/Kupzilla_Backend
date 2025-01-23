from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from app.services.category_service import CategoryService

category_api_blueprint = Blueprint('category_api', __name__)
api = Api(category_api_blueprint)

class CategoryResource(Resource):
    def get(self, category_id):
        category = CategoryService.get_category_by_id(category_id)
        if category:
            return jsonify(category.serialize())
        return {'message': 'Category not found'}, 404

    def put(self, category_id):
        data = request.get_json()
        category = CategoryService.update_category(category_id, data['name'])
        if category:
            return jsonify(category.serialize())
        return {'message': 'Category not found or update failed'}, 404

    def delete(self, category_id):
        if CategoryService.delete_category(category_id):
            return {'message': 'Category deleted'}, 200
        return {'message': 'Category not found'}, 404

class CategoryListResource(Resource):
    def get(self):
        categories = CategoryService.get_all_categories()
        return jsonify([category.serialize() for category in categories])

    def post(self):
        data = request.get_json()
        category = CategoryService.create_category(data['name'])
        return jsonify(category.serialize())

api.add_resource(CategoryResource, '/categories/<int:category_id>')
api.add_resource(CategoryListResource, '/categories')