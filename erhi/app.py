from flask import Flask
from flask_restful import Api
from erhi.resources.ping import Ping


app = Flask(__name__)
api = Api(app)

api.add_resource(Ping, '/ping')

if __name__ == '__main__':
    app.run()
