from flask import request, abort
from flask_restplus import Namespace, Resource
from mongoengine.errors import ValidationError

from erhi.models import auth, User

api = Namespace('user', description='')


@api.route('/')
class Profile(Resource):
    def get(self):
        # locate user with either object id or username
        id = request.args.get('id')
        # not a good idea to expose username in url
        # should add admin access only?
        username = request.args.get('username')

        if not id and not username:
            abort(400, 'id or username is required for user profile')

        user = None
        if id:
            user = User.objects(id=id).first()
        else:
            user = User.objects(username=username).first()

        if not user:
            abort(400, 'can not locate the user')

        # return user info plus event created as default
        # TODO: events created pagination
        profile = {
            'user_id': str(user.id),
            'email': user.email,
            'username': user.username,
            'created': [created.to_json() for created in user.created]
        }

        return profile


@api.route('/remove')
class UserDelete(Resource):
    @auth.login_required
    def post(self):
        id = request.args.get('id')
        username = request.args.get('username')

        if not id and not username:
            abort(400, 'id or username is required to delete user')

        try:
            if id:
                user = User.objects(id=id).first()
            else:
                user = user.objects(username=username).first()
        except ValidationError:
            abort(400, 'invalid user object id, it must be a 12-byte'
                       ' input or a 24-character hex string')

        if not user:
            abort(400, 'can not locate the user')

        user.delete()

        return {
            'message': 'user {} was deleted'.format(id if id else username)
        }
