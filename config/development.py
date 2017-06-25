import os

basedir = os.path.abspath(os.path.dirname(__file__))

APP_NAME = 'erhi'
SECRET_KEY = os.environ.get('SECRET_KEY') or 'cai-bu-dao-ba'

DEBUG = True

# DB
MONGODB_SETTINGS = {'DB': 'erhi'}
