import base64
import io
from PIL import Image
import os
from flask import url_for

class ImageManager:
    def __init__(self, upload_folder='upload_image'):
        self.upload_folder = upload_folder
        self.categories = ['users', 'promotions', 'branches', 'media_utils']
        
        # Crear la carpeta principal y las subcarpetas si no existen
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)

        for category in self.categories:
            category_folder = os.path.join(self.upload_folder, category)
            if not os.path.exists(category_folder):
                os.makedirs(category_folder)

    def upload_image(self, image_base64, filename, category):
    # Decodificar la imagen desde base64
        try:
            image_data = base64.b64decode(image_base64)
        except Exception as e:
            raise ValueError("Failed to decode Base64 image data") from e

        # Verificar que los datos decodificados son una imagen válida
        try:
            image = Image.open(io.BytesIO(image_data))
            image.load()  # Cargar la imagen en memoria completamente
        except Exception as e:
            raise ValueError("Decoded data is not a valid image file") from e

        # Redimensionar la imagen si es necesario
        resized_image = self.resize_image(image)

        # Verificar si la categoría es válida
        if category not in self.categories:
            raise ValueError(f"Invalid category: {category}. Must be one of {self.categories}")

        # Definir la ruta de la carpeta
        category_folder = os.path.join(self.upload_folder, category)
        print("category folder_____", category_folder, "filename_____", filename)

        # Extraer solo el nombre de archivo
        clean_filename = os.path.basename(filename)

        # Crear la carpeta de usuario o sucursal si no existe
        user_folder = os.path.join(category_folder, os.path.basename(os.path.dirname(filename)))

        # Si la categoría es 'users' o 'branches', utilizamos el identificador único
        if category == 'users':
            # Utiliza el email del usuario para crear la carpeta
            user_folder = os.path.join(category_folder, os.path.basename(os.path.dirname(filename)))
        elif category == 'branches':
            # Utiliza el partner_id o nombre de sucursal como subcarpeta
            partner_id = os.path.basename(os.path.dirname(filename))  # Extrae el identificador de la sucursal
            user_folder = os.path.join(category_folder, partner_id)

        # Crear la carpeta si no existe
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
        else:
            # Vaciar la carpeta si la categoría es 'users' o 'branches'
            if category in ['users', 'branches']:
                for file in os.listdir(user_folder):
                    file_path = os.path.join(user_folder, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        
        # Definir la ruta completa del archivo
        file_path = os.path.join(user_folder, clean_filename)
        print("file path, ",  file_path)
        # Guardar la imagen en el sistema de archivos en formato PNG
        try:
            resized_image.save(file_path, format='PNG')
        except Exception as e:
            raise ValueError(f"Failed to save image: {str(e)}")

        # Generar la URL para acceder a la imagen
        print("user_folder que se pasa para crear", user_folder)
        image_url = f"/upload_image/{category}/{os.path.basename(user_folder).replace('\\', '/')}/{clean_filename}"


        print("url de la nueva imagen", image_url)

        return image_url

    def resize_image(self, image, max_size=(500, 500)):
        """Redimensiona la imagen manteniendo la relación de aspecto."""
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        return image
    
    def delete_image(self, filename, category):
        """Elimina una imagen de la carpeta específica."""
        file_path = os.path.join(self.upload_folder, category, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        else:
            return False



# import base64
# import io
# from google.cloud import storage
# from PIL import Image
# import os
# import google.auth
# from config import Config

# class ImageManager:
#     def __init__(self):
#         self.bucket_name = Config.GCS_BUCKET_NAME

#         # Utiliza las credenciales desde Config.GOOGLE_CREDENTIALS
#         # print("imprimiendo credenciales",Config.GOOGLE_CREDENTIALS)

#         self.client = storage.Client.from_service_account_info(Config.GOOGLE_CREDENTIALS)

#         self.bucket = self.client.get_bucket(self.bucket_name)

#     def upload_image(self, image_base64, filename):
#         # Decodificar la imagen desde base64
#         try:
#             image_data = base64.b64decode(image_base64)
#         except Exception as e:
#             raise ValueError("Failed to decode Base64 image data") from e
        
#         # Verificar que los datos decodificados son una imagen válida
#         try:
#             image = Image.open(io.BytesIO(image_data))
#             image.load()  # Carga la imagen en memoria completamente
#         except Exception as e:
#             raise ValueError("Decoded data is not a valid image file") from e

#         # Redimensionar la imagen si es necesario
#         resized_image = self.resize_image(image)

#         # Subir la imagen redimensionada a Google Cloud Storage
#         blob = self.bucket.blob(filename)
#         output = io.BytesIO()
#         resized_image.save(output, format='PNG')
#         output.seek(0)
#         blob.upload_from_file(output, content_type='image/png')

#         # Hacer pública la imagen
#         blob.make_public()

#         # Devolver la URL pública de la imagen
#         return blob.public_url

#     def resize_image(self, image, max_size=(800, 800)):
#         image.thumbnail(max_size, Image.Resampling.LANCZOS)
#         return image
    
#     def delete_image(self, filename):
#         """Elimina una imagen del bucket de Google Cloud Storage"""
#         blob = self.bucket.blob(filename)
#         if blob.exists():
#             blob.delete()
#             return True
#         else:
#             return False

