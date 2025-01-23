from flask import Blueprint, Response, jsonify, current_app
from flask_restful import Api, Resource
import os

# Crear blueprint y API
image_api_blueprint = Blueprint('image_api', __name__)
api = Api(image_api_blueprint)

class ImageResource(Resource):
    def get(self, filename):
        # Definir la ruta completa
        file_path = os.path.join('upload_image', filename)
        print(f"Ruta completa: {file_path}")
        print("filename____", filename)
        print(os.path.exists(file_path))

        try:
            # Leer el archivo y devolverlo como respuesta
            with open(file_path, 'rb') as f:
                data = f.read()
            return Response(data, mimetype='image/png')
        except FileNotFoundError:
            return jsonify({"error": "Archivo no encontrado"}), 404
        except Exception as e:
            return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

# Agregar el recurso a la API
api.add_resource(ImageResource, '/upload_image/<path:filename>')