from flask import request, abort
from flask_restplus import Namespace, Resource

from erhi.models import User

api = Namespace('signup', description='')


@api.route('/')
class Signup(Resource):
    def post(self):
        # request header Content-Type must be set
        # to application/json for this to work
        data = request.get_json()

        email = data.get('email')
        password = data.get('password')
        if email is None or password is None:
            abort(400, 'both email and password are required for sign up')

        if User.objects(email=email).count():
            abort(400, 'existing user')  # existing user

        user = User(email=email)
        user.hash_password(password)

        user.save()

        return {'email': user.email}, 201
