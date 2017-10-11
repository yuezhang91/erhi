import os

basedir = os.path.abspath(os.path.dirname(__file__))

APP_NAME = 'erhi'
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = False

# DB
MONGODB_SETTINGS = {
    'db': 'erhi',
    'host': os.environ.get('MONGODB_URI')
}
