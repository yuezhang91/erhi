from flask import Flask
from flask_restplus import Api

app = Flask(__name__, instance_relative_config=True)
# TODO: load config based on env variable
app.config.from_object('config.development')
# sensitive config
app.config.from_pyfile('config.py')

api = Api(app)

# import models and resources after app
# initialization to prevent circular import
from erhi.models import db # noqa

db.init_app(app)


from erhi.resources.ping import api as Ping # noqa
from erhi.resources.signup import api as Signup # noqa
from erhi.resources.login import api as Login # noqa

api.add_namespace(Ping, '/ping')
api.add_namespace(Signup, '/signup')
api.add_namespace(Login, '/login')

if __name__ == '__main__':
    app.run()
