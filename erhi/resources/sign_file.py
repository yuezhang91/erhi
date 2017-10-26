from flask_restplus import Namespace, Resource, reqparse

import boto3

from erhi.app import app
from erhi.models import auth

api = Namespace('sign_file', description='S3 uploading signature')

parser = reqparse.RequestParser()
parser.add_argument('fname', type=str, required=True,
                    help='file name')
parser.add_argument('ftype', type=str, required=True,
                    help='file type')


@api.route('/')
class SignImageS3(Resource):
    @auth.login_required
    @api.expect(parser)
    def get(self):
        # We should pass in one more parameter to indicate the s3 bucket
        # say 'profile' then the profile bucket should be used
        S3_BUCKET = app.config['S3_BUCKET']

        args = parser.parse_args()
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
                s3_bucket=S3_BUCKET, file_name=file_name)
        }
