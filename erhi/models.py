from flask import g
from flask_mongoengine import MongoEngine
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pw_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from erhi.app import app

db = MongoEngine()
auth = HTTPBasicAuth()


class User(db.Document):
    email = db.StringField()
    password = db.StringField()

    def hash_password(self, raw_password):
        self.password = pw_context.encrypt(raw_password)

    def verify_password(self, raw_password):
        return pw_context.verify(raw_password, self.password)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'email': self.email})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        user = User.objects(email=data['email']).first()
        return user


@auth.verify_password
def verify_password(email_or_token, password):
    # try to authenticate by token
    user = User.verify_auth_token(email_or_token)
    if not user:
        user = User.objects(email=email_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True