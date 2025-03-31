from flask import Blueprint, jsonify
from flask_restful import Api, Resource
from app.services.country_city_service import CountryCityService
from app.models import City

countries_api_blueprint = Blueprint('countries_api', __name__)
api = Api(countries_api_blueprint)

class CountryListResource(Resource):
    def get(self):
        countries = CountryCityService.get_all_countries()
        return jsonify([country.serialize() for country in countries])

class CityListResource(Resource):
    def get(self, country_id):
        cities = CountryCityService.get_cities_by_country(country_id)
        return jsonify([city.serialize() for city in cities])

api.add_resource(CountryListResource, '/countries')
api.add_resource(CityListResource, '/countries/<int:country_id>/cities')