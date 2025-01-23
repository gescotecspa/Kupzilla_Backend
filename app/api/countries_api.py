from flask import Blueprint, jsonify
from flask_restful import Api, Resource
from app.services.country_service import CountryService

countries_api_blueprint = Blueprint('countries_api', __name__)
api = Api(countries_api_blueprint)

class CountryListResource(Resource):
    def get(self):
        countries = CountryService.get_all_countries()
        return jsonify([country.serialize() for country in countries])

api.add_resource(CountryListResource, '/countries')
