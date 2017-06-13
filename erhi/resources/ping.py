from flask_restplus import Resource


class Ping(Resource):
    def get(self):
        return {'ping': 'pong'}
