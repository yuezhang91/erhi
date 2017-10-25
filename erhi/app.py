import os

from flask import Flask
from flask_restplus import Api

app = Flask(__name__, instance_relative_config=True)

env = os.environ.get('FLASK_ENV')
try:
    app.config.from_object('config.{env}'.format(env=env))
except ImportError:
    # default to development environment
    # TODO: add info to log
    # app.logger.info('environment variable {env} invalid, \
    #     default to development'.format(env=env))
    app.config.from_object('config.development')

# sensitive config
app.config.from_pyfile('config.py')

api = Api(app,
          version='1.0',
          title='Hier API')

# import models and resources after app
# initialization to prevent circular import
from erhi.models import db # noqa

db.init_app(app)


from erhi.resources.ping import api as Ping # noqa
from erhi.resources.signup import api as Signup # noqa
from erhi.resources.login import api as Login # noqa
from erhi.resources.user import api as User # noqa
from erhi.resources.events import api as Events # noqa
from erhi.resources.sign_file import api as SignFile # noqa

api.add_namespace(Ping, '/ping')

api.add_namespace(Signup, '/signup')
api.add_namespace(Login, '/login')
api.add_namespace(User, '/user')

api.add_namespace(Events, '/events')

api.add_namespace(SignFile, '/sign_file')

if __name__ == '__main__':
    port = int(os.environ.get('PORT') or 5000)
    app.run(host='0.0.0.0', port=port)
