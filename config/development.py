import os

basedir = os.path.abspath(os.path.dirname(__file__))

APP_NAME = 'erhi'
SECRET_KEY = os.environ.get('SECRET_KEY') or 'cai-bu-dao-ba'
DEBUG = True

S3_BUCKET = 'hier-profile-images-development'

# DB
MONGODB_SETTINGS = {'db': 'erhi'}

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY') or 'random'
