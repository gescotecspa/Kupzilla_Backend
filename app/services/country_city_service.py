import os
from dotenv import load_dotenv
import requests
from app import db
from app.models import Country, City
from sqlalchemy import asc

load_dotenv()
# Cargar las variables de entorno desde el archivo .env
class CountryCityService:
    @staticmethod
    def load_countries_and_cities():
        print("Saltando la obtención de países desde la API, usando base de datos local.")
        
        # continentl_api_key = os.getenv("CONTINENTL_API_KEY")
        # geonames_username = os.getenv("GEONAMES_USERNAME")
        # print("apikey", continentl_api_key, "username", geonames_username)
        
        # Obtén todos los países desde la API de continentl
        # url = f"https://continentl.com/api/country-list?page=1&key={continentl_api_key}"
        # try:
        #     response = requests.get(url)
        #     response.raise_for_status()  # Esto lanza un error si la respuesta no es 200
        # except requests.exceptions.RequestException as e:
        #     print(f"Error al obtener los países: {e}")
        #     return

        # if response.status_code == 200:
        #     countries_data = response.json() 
        #     if not countries_data:
        #         print("No se encontraron países en la respuesta.")
        #         return

        #     for country_data in countries_data:
        #         country_name = country_data.get('name')
        #         country_code = country_data.get('code')
        #         country_phone_code = country_data.get('country-code')

        #         # Agrega el país si no existe
        #         existing_country = Country.query.filter_by(code=country_code).first()
        #         if not existing_country:
        #             new_country = Country(
        #                 name=country_name,
        #                 code=country_code,
        #                 phone_code=country_phone_code
        #             )
        #             db.session.add(new_country)
        #             db.session.commit()
        #             print(f"País {country_name} cargado exitosamente.")

        #             # Ahora cargamos las ciudades usando GeoNames
        #             geo_url = f"http://api.geonames.org/searchJSON?country={country_code}&maxRows=1000&username={geonames_username}"
        #             try:
        #                 geo_response = requests.get(geo_url)
        #                 geo_response.raise_for_status()
        #             except requests.exceptions.RequestException as e:
        #                 print(f"Error al obtener las ciudades de {country_name}: {e}")
        #                 continue

        #             if geo_response.status_code == 200:
        #                 cities_data = geo_response.json().get('geonames', [])
        #                 if not cities_data:
        #                     print(f"No se encontraron ciudades para {country_name}.")
        #                 for city_data in cities_data:
        #                     city_name = city_data.get('name')
        #                     city_latitude = city_data.get('lat')
        #                     city_longitude = city_data.get('lng')

        #                     # Verificar si la ciudad ya existe
        #                     existing_city = City.query.filter_by(name=city_name, country_id=new_country.id).first()
        #                     if not existing_city:
        #                         new_city = City(
        #                             name=city_name,
        #                             latitude=city_latitude,
        #                             longitude=city_longitude,
        #                             country_id=new_country.id
        #                         )
        #                         db.session.add(new_city)
        #                         db.session.commit()
        #                         print(f"Ciudad {city_name} agregada exitosamente.")
        #                     else:
        #                         print(f"La ciudad {city_name} ya existe en la base de datos.")
        #             else:
        #                 print(f"Error al obtener las ciudades de {country_name}: {geo_response.status_code}")
        #         else:
        #             print(f"El país {country_name} ya existe en la base de datos.")
        # else:
        #     print(f"Error al obtener los países: {response.status_code}")

    @staticmethod
    def get_all_countries():
        return Country.query.order_by(asc(Country.name)).all()
    
    @staticmethod
    def get_cities_by_country(country_id):
        return City.query.filter_by(country_id=country_id).order_by(asc(City.name)).all()
