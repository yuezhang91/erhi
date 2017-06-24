from flask import Flask
from flask_restplus import Api

from erhi.resources.ping import api as Ping
from erhi.resources.signup import api as Signup
from erhi.resources.login import api as Login

from erhi.models import db


app = Flask(__name__)
app.config['SECRET_KEY'] = 'erhiforhier'
app.config['MONGODB_SETTINGS'] = {'DB': 'erhi'}

api = Api(app)

db.init_app(app)

api.add_namespace(Ping, '/ping')
api.add_namespace(Signup, '/signup')
api.add_namespace(Login, '/login')

if __name__ == '__main__':
    app.run()
