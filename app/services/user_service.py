from app.models.city import City
from app.models.country import Country
from app.models.user import User
from app import db
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from ..common.email_utils import send_email
from flask import render_template
from ..common.pdf_utils import generate_pdf
from ..common.image_manager import ImageManager
import uuid
from app.models.status import Status
from datetime import datetime
from app.models.terms_and_conditions import TermsAndConditions
from sqlalchemy import func

class UserService:
    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_email(email: str):
        # Busca el usuario por email y que el status no sea "deleted"
        return User.query.join(User.status).filter(
            func.lower(User.email) == func.lower(email),
            User.status.has(name='deleted') == False
        ).first()

    @staticmethod
    def get_all_users():
        return User.query.all()

    @staticmethod
    def create_user(password, first_name, last_name, country, email, status_id, city=None, birth_date=None, phone_number=None, gender=None, subscribed_to_newsletter=None, image_data=None, accept_terms=False):
        existing_user = UserService.get_user_by_email(email)
        print(existing_user)
        if existing_user and existing_user.status.name != 'deleted':
            raise ValueError("A user with that email already exists.")

        if not accept_terms:
            raise ValueError("Debe aceptar los términos y condiciones.")

        hashed_password = generate_password_hash(password)
        
        # Manejo de la imagen con ImageManager
        image_url = None
        if image_data:
            image_manager = ImageManager()
            filename = f"users/{email}/profile_image.png"
            category = 'users'
            image_url = image_manager.upload_image(image_data, filename, category)
        status = Status.query.get(status_id)
        if not status:
            raise ValueError("Invalid status ID provided.")
        
        # Obtener el último término y condiciones creados
        latest_terms = TermsAndConditions.query.order_by(TermsAndConditions.id.desc()).first()
        if not latest_terms:
            raise ValueError("No terms and conditions available.")

        # Buscar el país usando el ID
        country_obj = Country.query.get(country)  # Usamos 'get' para obtener el objeto por ID
        if not country_obj:
            raise ValueError("Invalid country ID provided.")
        
        # Buscar la ciudad usando el ID
        city_obj = None
        if city:
            city_obj = City.query.get(city)  # Usamos 'get' para obtener el objeto por ID
            if not city_obj:
                raise ValueError("Invalid city ID provided.")
        
        new_user = User(
            password=hashed_password, 
            first_name=first_name, 
            last_name=last_name, 
            country=country_obj,
            email=email, 
            status=status, 
            city=city_obj,
            birth_date=birth_date, 
            phone_number=phone_number, 
            gender=gender, 
            subscribed_to_newsletter=subscribed_to_newsletter, 
            image_url=image_url,
            terms_id=latest_terms.id,
            terms_accepted_at=datetime.utcnow()
        )
        db.session.add(new_user)
        try:
            db.session.commit()
            
            # Generar PDF con QR
            pdf_buffer = generate_pdf(f"{first_name} {last_name}", email, new_user.user_id)
            pdf_filename = f"Credential_{first_name}_{last_name}.pdf"
            
            # Enviar correo electrónico de bienvenida usando una plantilla HTML
            subject = "Bienvenido a nuestra aplicación! Kupzilla"
            recipients = [email]
            html_body = render_template('email/welcome_email.html', email=email, first_name=first_name)
            send_email(subject, recipients, html_body, pdf_buffer, pdf_filename)

        except IntegrityError:
            db.session.rollback()
            raise ValueError("A database error occurred, possibly duplicated data.")
        return new_user
    
    @staticmethod
    def update_user(user_id, **kwargs):
        user = UserService.get_user_by_id(user_id)
        print("usuario Buscado", user)
        
        # Verificar si se encuentra el usuario
        if user:
            # Manejo de la imagen con ImageManager en la actualización
            if 'image_data' in kwargs:
                image_data = kwargs.pop('image_data')
                if image_data:
                    try:
                        image_manager = ImageManager()
                        unique_id = uuid.uuid4().hex
                        filename = f"users/{user.email}/profile_image_{unique_id}.png"
                        category = 'users'
                        image_url = image_manager.upload_image(image_data, filename, category)
                        user.image_url = image_url
                    except Exception as e:
                        print(f"Error al subir la imagen: {e}")
                        return {'message': 'Error al subir la imagen'}, 500

            # Asignación de Country
            if 'country' in kwargs:
                country_id = kwargs.pop('country')
                country = Country.query.get(country_id)
                if country:
                    user.country = country
                else:
                    raise ValueError(f"El país con ID {country_id} no existe.")

            # Asignación de City
            if 'city' in kwargs:
                city_id = kwargs.pop('city')
                city = City.query.get(city_id)
                if city:
                    user.city = city
                else:
                    raise ValueError(f"La ciudad con ID {city_id} no existe.")

            # Manejo de la actualización de la contraseña
            if 'password' in kwargs:
                new_password = kwargs.pop('password')
                current_password = kwargs.pop('current_password', None)

                if not current_password:
                    # La contraseña actual no fue proporcionada
                    raise ValueError("Se requiere la contraseña actual para cambiar la contraseña.")

                # Verificar si la contraseña actual es correcta
                if not check_password_hash(user.password, current_password):
                    # La contraseña actual no coincide
                    raise ValueError("La contraseña actual es incorrecta.")

                # Encriptar la nueva contraseña y actualizarla
                hashed_password = generate_password_hash(new_password)
                user.password = hashed_password

            # Actualizar otros campos del usuario
            for key, value in kwargs.items():
                setattr(user, key, value)

            # Confirmar los cambios en la base de datos
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error al hacer commit: {e}")
                return {'message': 'Error al actualizar el usuario'}, 500

            return user

        return None

    @staticmethod
    def delete_user(user_id):
        user = UserService.get_user_by_id(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False

    @staticmethod
    def create_user_partner(password, first_name, last_name, country, email, status_id, city=None, birth_date=None, phone_number=None, gender=None, subscribed_to_newsletter=None):
        existing_user = UserService.get_user_by_email(email)
        if existing_user and existing_user.status.name != 'deleted':
            raise ValueError("A user with that email already exists.")

        hashed_password = generate_password_hash(password)
        
        # Manejo de la imagen con ImageManager
        image_url = None
        
        status = Status.query.get(status_id)
        if not status:
            raise ValueError("Invalid status ID provided.")
        
        new_user = User(
            password=hashed_password, 
            first_name=first_name, 
            last_name=last_name, 
            country=country, 
            email=email, 
            status=status, 
            city=city, 
            birth_date=birth_date, 
            phone_number=phone_number, 
            gender=gender, 
            subscribed_to_newsletter=subscribed_to_newsletter, 
            image_url=image_url
        )
        db.session.add(new_user)
        try:
            db.session.commit()
            
            # Generar PDF con QR
            # pdf_buffer = generate_pdf(f"{first_name} {last_name}", email)
            # pdf_filename = f"Credential_{first_name}_{last_name}.pdf"
            
            # Enviar correo electrónico de bienvenida usando una plantilla HTML
            subject = "Bienvenido a nuestra aplicación! KuplizzApp"
            recipients = [email]
            html_body = render_template('email/welcome_email_partner.html', email=email, first_name=first_name, password=password )
            send_email(subject, recipients, html_body)

        except IntegrityError:
            db.session.rollback()
            raise ValueError("A database error occurred, possibly duplicated data.")
        return new_user