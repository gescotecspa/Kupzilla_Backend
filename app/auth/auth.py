from flask import Blueprint, request, jsonify, make_response, current_app, render_template
from flask_restful import abort as rest_abort
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
import uuid
import random
import string
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from ..models.user import User
from ..services.user_service import UserService
from ..common.email_utils import send_email
from datetime import datetime, timedelta, timezone
import os
from app import db

auth_blueprint = Blueprint('auth', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        is_token_required = os.getenv("token_required", False)

        token = None

        # 🔹 Verificar si la cabecera Authorization está presente
        if 'Authorization' in request.headers:
            parts = request.headers['Authorization'].split()
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                return jsonify({"message": "Token is missing or improperly formatted"}), 401  # 🔹 Respuesta en JSON
            token = parts[1]

        if not token:
            if is_token_required == "True":
                return jsonify({"message": "Token is missing!"}), 401  # 🔹 Mensaje corregido
            else:
                kwargs['current_user'] = None
                return f(*args, **kwargs)

        # 🔹 Si hay token, lo validamos
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])

            # 🔹 Verificar si es un token de invitado
            if data.get("is_guest"):
                current_user = {"is_guest": True, "guest_id": data.get("guest_id")}
            else:
                current_user = User.query.filter_by(email=data.get('email')).first()
                if not current_user:
                    return jsonify({"message": "User not found!"}), 404  # 🔹 Manejo de usuario no encontrado
            
            kwargs['current_user'] = current_user

        except jwt.ExpiredSignatureError:
            return make_response(jsonify({"message": "Token has expired!"}), 401) # 🔹 Expiración del token
        except jwt.InvalidTokenError:
            return make_response(jsonify({"message": "Token is invalid!"}), 401)  # 🔹 Token inválido
        except Exception as e:
            return make_response(jsonify({"message": f"Error al validar el token: {str(e)}"}), 500)  # 🔹 Error inesperado

        return f(*args, **kwargs)

    return decorated

# =====================================
# RUTAS DE AUTENTICACIÓN
# =====================================

@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Debe ingresar email y contraseña'}), 400

    print(data['email'], data['password'])
    
    platform = data.get('platform')
    print(platform)
    if platform and platform != "android" and platform != "ios":
        return jsonify({'message': 'Plataforma incorrecta'}), 400

    # Obtener el usuario por email

    user = UserService.get_user_by_email(data['email'])
    if not user:
        return jsonify({'message': 'No existe el usuario'}), 404

    if check_password_hash(user.password, data['password']):
        try:

            # Registrar fecha de login (ahora con zona horaria UTC explícita)
            user.last_login_at = datetime.now(timezone.utc)

            # Registrar versión de la app y plataforma, si están presentes
            user.app_version = data.get('app_version', user.app_version) 
            user.platform = data.get('platform', user.platform)

            # Guardar cambios en la base de datos
            db.session.commit()

            # Generar el token JWT
            token = jwt.encode(
                {
                    'email': user.email,
                    'exp': datetime.now(timezone.utc) + timedelta(hours=3)
                },
                current_app.config['SECRET_KEY'],
                algorithm="HS256"
            )

            if isinstance(token, bytes):
                token = token.decode('utf-8')
            return jsonify({'token': token, 'user': user.serialize()}), 200

        except Exception as e:
            db.session.rollback()  # Deshacer cambios en caso de error
            return jsonify({'message': f'Error al procesar el login: {str(e)}'}), 500

    return jsonify({'message': 'Contraseña inválida'}), 401


@auth_blueprint.route('/guest-login', methods=['POST'])
def guest_login():
        # Generar un identificador único para el invitado
    guest_id = str(uuid.uuid4())
    expiration_time = datetime.now(timezone.utc) + timedelta(hours=24)

        # Crear el payload del token
    payload = {
            "is_guest": True,
            "guest_id": guest_id,
            "exp": expiration_time
        }

        # Generar el token
    try:
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm="HS256")
        if isinstance(token, bytes):
                token = token.decode('utf-8')
        return jsonify({"guest_token": token}), 200
    except Exception as e:
        return jsonify({"message": f"Error al generar el token: {str(e)}"}), 500
        

@auth_blueprint.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    image_data = data.pop('image_data', None)

    try:
        if not data.get('accept_terms'):
            return jsonify({'message': 'Debe aceptar los términos y condiciones'}), 400

        user = UserService.create_user(**data, image_data=image_data)
        return jsonify(user.serialize()), 201
    except ValueError as e:
        return {'message': str(e)}, 400


# =====================================
# RUTAS QUE DEPENDEN DE LA VARIABLE token_required
# =====================================

@auth_blueprint.route('/user', methods=['GET'])
@token_required
def get_user(current_user):
    if current_user is None:
        return jsonify({"message": "No hay usuario autenticado."}), 401  # 🔹 Manejo del caso sin usuario

    if isinstance(current_user, dict):  # Si es invitado
        if current_user.get("is_guest"):
            return jsonify({"message": "Acceso denegado: solo usuarios registrados pueden acceder a esta ruta."}), 403

    return jsonify(current_user.serialize())



@auth_blueprint.route('/users', methods=['GET'])
@token_required
def get_all_users(current_user=None):

    if current_user is None:
        # Sin token (modo antiguo)
        return jsonify({"message": "Debes ingresar un token para solicitar los usuarios."}), 200
    
    if isinstance(current_user, dict) and current_user.get('is_guest'):
        return {"message": "Invitado no puede ver la lista completa de usuarios."}, 403
    
    # Usuario registrado con token
    users = UserService.get_all_users()
    return jsonify([user.serialize() for user in users]), 200


# =====================================
# RUTAS QUE REALMENTE REQUIEREN TOKEN
# (p.ej., acceso crítico)
# =====================================
@auth_blueprint.route('/user/<int:user_id>', methods=['PUT'])
@token_required
def update_user(current_user, user_id):
    """
    Si token_required = "false" en .env, este endpoint igual permite "pasar sin token"???
    - Con esta configuración actual, sí. Depende de lo que quieras hacer.
    - Si deseas forzar el token para ciertos endpoints aunque el .env diga "false",
      deberías cambiar la lógica o tener otro decorador.
    """
    if current_user is None:
        # Lógica si se permite sin token (solo cuando .env="false")
        return {"message": "No tienes token para actualizar usuario."}, 403

    data = request.get_json()
    image_data = data.pop('image_data', None)

    user = UserService.update_user(user_id, **data, image_data=image_data)
    if user:
        return jsonify(user.serialize())
    return {'message': 'User not found'}, 404

# Restablecer contraseña
def generate_reset_code(length=8):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

@auth_blueprint.route('/reset_password', methods=['POST'])
def reset_password_request():
    data = request.get_json()
    email = data.get('email')

    user = UserService.get_user_by_email(email)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    reset_code = generate_reset_code()
    user.reset_code = reset_code
    user.reset_code_expiration = datetime.utcnow() + timedelta(hours=1)
    db.session.commit()

    reset_url = "https://kupzilla.com/reset_password"
    subject = "Recuperación de contraseña - Kupzilla"
    recipients = [email]
    html_body = render_template('email/reset_password.html', reset_code=reset_code, reset_url=reset_url)

    send_email(subject, recipients, html_body)

    return jsonify({'message': 'Password reset email sent'}), 200

@auth_blueprint.route('/reset_password/new_password', methods=['PUT'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')
    new_password = data.get('password')

    user = UserService.get_user_by_email(email)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if user.reset_code != code or user.reset_code_expiration < datetime.utcnow():
        return jsonify({'message': 'Invalid or expired reset code'}), 400

    hashed_password = generate_password_hash(new_password)
    user.password = hashed_password
    user.reset_code = None
    user.reset_code_expiration = None
    db.session.commit()

    return jsonify({'message': 'Password has been reset'}), 200


@auth_blueprint.route('/signup-partner', methods=['POST'])
@token_required
def signup_partner(current_user):
    if current_user is None:
        return {"message": "No puedes registrar un asociado sin el token correspondiente"}, 403

    data = request.get_json()
    image_data = data.pop('image_data', None)
    
    try:
        user = UserService.create_user_partner(**data)
        return jsonify(user.serialize()), 201
    except ValueError as e:
        return {'message': str(e)}, 400


# =====================================
# BULK CREATION (también protegidas)
# =====================================
@auth_blueprint.route('/signup/bulk', methods=['POST'])
@token_required
def create_bulk_users(current_user):
    if current_user is None:
        return {"message": "No token, acción no permitida"}, 403

    data = request.get_json()
    if not isinstance(data, list):
        return {'message': 'Invalid data format. Expected a list of users.'}, 400

    created_users = []
    errors = []

    for user_data in data:
        image_data = user_data.pop('image_data', None)
        try:
            user = UserService.create_user(**user_data, image_data=image_data)
            created_users.append(user.serialize())
        except ValueError as e:
            errors.append({'user_data': user_data, 'error': str(e)})

    if errors:
        return jsonify({'created_users': created_users, 'errors': errors}), 207
    return jsonify({'created_users': created_users}), 201


@auth_blueprint.route('/signup-partners/bulk', methods=['POST'])
@token_required
def signup_partners(current_user):
    if current_user is None:
        return {"message": "No token, acción no permitida"}, 403

    data = request.get_json()
    if not isinstance(data, list):
        return {'message': 'Invalid data format. Expected a list of partners.'}, 400

    created_users = []
    errors = []

    for partner_data in data:
        try:
            user = UserService.create_user_partner(**partner_data)
            created_users.append(user.serialize())
        except ValueError as e:
            errors.append({'partner_data': partner_data, 'error': str(e)})

    if errors:
        return jsonify({
            'created_users': created_users,
            'errors': errors
        }), 400

    return jsonify({
        'created_users': created_users
    }), 201
