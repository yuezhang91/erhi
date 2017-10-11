from flask import abort
from flask_restplus import Namespace, Resource, reqparse, fields
from mongoengine.errors import ValidationError

import boto3

from erhi.app import app
from erhi.models import auth, User
from erhi.resources.events import event_fields

api = Namespace('user', description='user profile')

# response marshalling
user_fields = api.model('User', {
    'id': fields.String,
    'email': fields.String,
    'username': fields.String,
    'created_events':
        fields.List(fields.Nested(event_fields), attribute='created'),
    'created_on': fields.DateTime(dt_format='rfc822')
})

user_parser = reqparse.RequestParser()
user_parser.add_argument('id', type=str, help='user object id')
user_parser.add_argument('username', type=str, help='unique user name')


@api.route('/')
class Profile(Resource):
    @auth.login_required
    @api.marshal_with(user_fields)
    @api.expect(user_parser)
    def get(self):
        # locate user with either object id or username
        args = user_parser.parse_args()
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
        args = user_parser.parse_args()
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


image_sign_parser = reqparse.RequestParser()
image_sign_parser.add_argument('fname', type=str, required=True,
                               help='image file name')
image_sign_parser.add_argument('ftype', type=str, required=True,
                               help='image file type')


@api.route('/sign_image')
class SignImageS3(Resource):
    @auth.login_required
    def get(self):
        S3_BUCKET = app.config['S3_BUCKET']

        args = image_sign_parser.parse_args()
        file_name = args['fname']
        file_type = args['ftype']

        s3 = boto3.client('s3')
        presigned_post = s3.generate_presigned_post(
            Bucket=S3_BUCKET,
            Key=file_name,
            Fields={"acl": "public-read", "Content-Type": file_type},
            Conditions=[
                {"acl": "public-read"},
                {"Content-Type": file_type}
            ],
            ExpiresIn=3600
        )

        return {
            'data': presigned_post,
            'url': 'https://{s3_bucket}.s3.amazonaws.com/{file_name}'.format(
                s3_bucket=S3_BUCKET, filename=file_name)
        }
