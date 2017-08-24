from flask import request, abort
from flask_restplus import Namespace, Resource, fields

from erhi.models import User

api = Namespace('signup', description='user signup')

signup_fields = api.model('Signup', {
    'email': fields.String(required=True),
    # TODO: how do we want to handle wechat login where the email is missing?
    # Do we want to force an unique username?
    'username': fields.String(),
    'password': fields.String(required=True)
})


@api.route('/')
class Signup(Resource):
    @api.expect(signup_fields, validate=True)
    def post(self):
        # request header Content-Type must be set
        # to application/json for this to work
        data = request.get_json()

        email = data.get('email')
        username = data.get('username') or email
        password = data.get('password')

        if User.objects(email=email).count():
            abort(400, 'existing user')  # existing user

        user = User(
            email=email,
            username=username)
        user.hash_password(password)

        user.save()

        return {'email': user.email}, 201
