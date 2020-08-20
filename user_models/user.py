from __init__ import db
from __main__ import app
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
import datetime
from flask import Flask, request, render_template_string,abort, jsonify, g, url_for
from flask_babelex import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_user import current_user, login_required, roles_required, UserManager, UserMixin



class User(db.Model, UserMixin):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

        # User authentication information. The collation='NOCASE' is required
        # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
        email = db.Column(db.String(255), nullable=False, unique=True)
        email_confirmed_at = db.Column(db.DateTime())
        password = db.Column(db.String(255), nullable=False, server_default='')

        # User information
        first_name = db.Column(db.String(100), nullable=False, server_default='')
        last_name = db.Column(db.String(100), nullable=False, server_default='')

        # Define the relationship to Role via UserRoles
        roles = db.relationship('Role', secondary='user_roles')


        def hash_password(self, password):
          self.password = pwd_context.encrypt(password)

        def verify_password(self, password):
          return pwd_context.verify(password, self.password)

        def generate_auth_token(self, expiration=False):
           s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
           return s.dumps({'id': self.id})

        @staticmethod
        def verify_auth_token(token):
          s = Serializer(app.config['SECRET_KEY'])
          try:
             data = s.loads(token)
          except SignatureExpired:
             return None    # valid token, but expired
          except BadSignature:
             return None    # invalid token
          user = User.query.get(data['id'])
          return user

class Role(db.Model):
        __tablename__ = 'roles'
        id = db.Column(db.Integer(), primary_key=True)
        name = db.Column(db.String(50), unique=True)

    # Define the UserRoles association table
class UserRoles(db.Model):
        __tablename__ = 'user_roles'
        id = db.Column(db.Integer(), primary_key=True)
        user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
        role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))
