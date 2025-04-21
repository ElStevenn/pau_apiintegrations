import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, 'secrets', '.env')
load_dotenv(ENV_PATH)

"""DATABASE"""
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'mydatabase')
DB_USERNAME = os.getenv('DB_USERNAME', 'myuser')
DB_PASSWORD = os.getenv('DB_PASSWD', 'mypassword')

"""AWS CREDENTIALS"""
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'mys3access')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'mys3secretkey')

"""OPENAI"""
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'myopenaiapikey')

"""SECURITY"""
def load_public_key(path):
    absolute_path = os.path.join(BASE_DIR, path)
    with open(absolute_path, 'rb') as public_key_file:
        public_key = serialization.load_pem_public_key(public_key_file.read())
    return public_key

def load_private_key(path):
    absolute_path = os.path.join(BASE_DIR, path)
    with open(absolute_path, 'rb') as private_key_file:
        private_key = serialization.load_pem_private_key(
            private_key_file.read(),
            password=None  
        )
    return private_key

JWT_SECRET_KEY = os.getenv('JWT_SECRET')
SECURITY_KEY = os.getenv('SECURITY_KEY')