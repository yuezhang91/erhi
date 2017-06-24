from flask_restplus import Namespace, Resource

api = Namespace('signup', description='')


@api.route('/')
class Ping(Resource):
    def get(self):
        return {'ping': 'pong'}
