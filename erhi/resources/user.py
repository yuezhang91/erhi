from flask import request, abort
from flask_restplus import Namespace, Resource

from erhi.models import User

api = Namespace('user', description='')


@api.route('/')
class Profile(Resource):
    def get(self):
        # locate user with either object id or username
        oid = request.args.get('oid')
        # not a good idea to expose username in url
        # should add admin access only?
        username = request.args.get('username')

        if not oid and not username:
            abort(400, 'oid or username is required for user profile')

        user = None
        if oid:
            user = User.objects(oid=oid).first()
        else:
            user = User.objects(username=username).first()

        if not user:
            abort(400, 'cannot locate the user')

        # return user info plus event created as default
        # TODO: events created pagination
        profile = {
            'user_id': str(user.id),
            'email': user.email,
            'username': user.username,
            'created': [created.to_json() for created in user.created]
        }

        return profile
