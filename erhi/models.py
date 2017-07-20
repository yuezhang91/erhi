from flask import g
from flask_mongoengine import MongoEngine
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pw_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from datetime import datetime

from erhi.app import app

db = MongoEngine()
auth = HTTPBasicAuth()


class User(db.Document):
    email = db.EmailField()
    username = db.StringField()
    password = db.StringField()
    created = db.DateTimeField()

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


class Event(db.Document):
    title = db.StringField()
    description = db.StringField()
    time = db.DateTimeField(required=True)
    # auto_index defaults to True, automatically create  a ‘2dsphere’ index
    location = db.PointField(required=True)
    creator = db.StringField()
    # default for ListFields is []
    keywords = db.ListField()
    created = db.DateTimeField(default=datetime.utcnow())
    updated = db.DateTimeField(default=datetime.utcnow())
