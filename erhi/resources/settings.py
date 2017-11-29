import sendgrid
from sendgrid.helpers.mail import Email, Content, Mail

from flask import request, abort
from flask_restplus import Namespace, Resource, fields

from erhi.app import app
from erhi.models import User

api = Namespace('settings', description='user settings')


forgot_password_fields = api.model('ForgotPassword', {
    'email': fields.String(required=True),
})


def sendForgotPasswordEmail(to_email):
    sg = sendgrid.SendGridAPIClient(apikey=app.config['SENDGRID_API_KEY'])
    from_email = Email('okilltheboring@gmail.com')
    subject = 'Reset Your Password for Hier'
    to_email = Email(to_email)
    content = Content("text/plain", "Just test it")
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())

    return response


@api.route('/forgot_password')
class ForgotPassword(Resource):
    @api.expect(forgot_password_fields, validate=True)
    def post(self):
        data = request.get_json()

        email = data.get('email')

        user = User.objects(email=email).first()

        if not user:
            abort(400, 'can not locate the user')

        return sendForgotPasswordEmail(user.email)
