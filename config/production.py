import os

basedir = os.path.abspath(os.path.dirname(__file__))

APP_NAME = 'erhi'
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = False

S3_BUCKET = 'hier-profile-images'

# DB
MONGODB_SETTINGS = {
    'db': 'erhi',
    'host': os.environ.get('MONGODB_URI')
}

# SendGrid API key
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
