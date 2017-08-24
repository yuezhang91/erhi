from flask import abort
from flask_restplus import Namespace, Resource, reqparse, fields
from mongoengine.errors import ValidationError

from erhi.models import auth, User
from erhi.resources.events import event_fields

api = Namespace('user', description='user profile')

parser = reqparse.RequestParser()
parser.add_argument('id', type=str, help='user object id')
parser.add_argument('username', type=str, help='unique user name')

# response marshalling
user_fields = api.model('User', {
    'id': fields.String,
    'email': fields.String,
    'username': fields.String,
    'created_events':
        fields.List(fields.Nested(event_fields), attribute='created'),
    'created_on': fields.DateTime(dt_format='rfc822')
})


@api.route('/')
class Profile(Resource):
    @api.marshal_with(user_fields)
    @api.expect(parser)
    def get(self):
        # locate user with either object id or username
        args = parser.parse_args()
        id = args['id']

        # not a good idea to expose username in url
        # should be admin access only?
        username = args['username']

        if not id and not username:
            abort(400, 'id or username is required for user profile')

        user = None
        if id:
            user = User.objects(id=id).first()
        else:
            user = User.objects(username=username).first()

        if not user:
            abort(400, 'can not locate the user')

        return user


@api.route('/remove')
class UserDelete(Resource):
    @auth.login_required
    def post(self):
        args = parser.parse_args()
        id = args['id']
        username = args['username']

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
