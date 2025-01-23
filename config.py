from dotenv import load_dotenv
import os

# Carga las variables de entorno desde el archivo .env
load_dotenv()
# print(os.getenv('SQLALCHEMY_DATABASE_URI'))
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    
    # Configuración de SMTP
    SMTP_SERVER = os.getenv('SMTP_SERVER')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    SMTP_DEFAULT_SENDER = os.getenv('SMTP_DEFAULT_SENDER')
    GCS_BUCKET_NAME = os.getenv('GCS_BUCKET_NAME', 'turismo-app-cobquecura')
    
    # GOOGLE_CREDENTIALS = {
    #     "type": os.getenv('GCP_TYPE'),
    #     "project_id": os.getenv('GCP_PROJECT_ID'),
    #     "private_key_id": os.getenv('GCP_PRIVATE_KEY_ID'),
    #     "private_key": os.getenv('GCP_PRIVATE_KEY').replace("\\n", "\n"),
    #     "client_email": os.getenv('GCP_SERVICE_ACCOUNT_EMAIL'),
    #     "client_id": os.getenv('GCP_CLIENT_ID'),
    #     "auth_uri": os.getenv('GCP_AUTH_URI'),
    #     "token_uri": os.getenv('GCP_TOKEN_URI'),
    #     "auth_provider_x509_cert_url": os.getenv('GCP_AUTH_PROVIDER_X509_CERT_URL'),
    #     "client_x509_cert_url": os.getenv('GCP_CLIENT_X509_CERT_URL')
    # }