from flask_restplus import Namespace, Resource

api = Namespace('ping', description='health check')


@api.route('/')
class Ping(Resource):
    def get(self):
        return {'ping': 'pong'}
