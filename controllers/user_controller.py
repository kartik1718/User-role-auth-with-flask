from __init__ import db
from __main__ import User, auth, app
from flask import Blueprint, abort, request, jsonify, g, url_for
import datetime
from flask import Flask, request, render_template_string,abort, jsonify, g, url_for
from flask_babelex import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_user import current_user, login_required, roles_required, UserManager, UserMixin
from user_models.user import Role,UserRoles,User


user_controller = Blueprint('user_controller', __name__)


@auth.verify_password
def verify_password(email_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(email_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(email=email_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

user_manager = UserManager(app, db, User)
db.create_all()
@app.route('/api/users', methods=['POST'])
def new_user():
    email = request.json.get('email')
    password = request.json.get('password')
    first_name = request.json.get('first_name')
    last_name=request.json.get('last_name')
    role=request.json.get('role')
    if email is None or password is None:
        abort(400)    # missing arguments
    if User.query.filter_by(email=email).first() is not None:
        abort(400)    # existing user
    user = User(email=email,first_name=first_name,last_name=last_name)
    user.hash_password(password)
    
    # Create 'member@example.com' user with no roles
    My_role = Role(name=role)
    
    user.roles.append(My_role)
    db.session.commit()
    db.session.add(user)
    db.session.commit()
    return (jsonify({'user_id': user.id, 'token': user.generate_auth_token(600).decode('ascii')}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})

@app.route('/api/users/signin', methods=['POST'])
@auth.login_required
def get_user():
    email = request.json.get('email')
    user = User.query.filter_by(email=email).first()
    userroles=UserRoles.query.filter_by(user_id=user.id).first()
    rols=Role.query.filter_by(id=userroles.role_id).first()
    if not user:
        abort(400)
    #return jsonify({'user_id': user.id, 'token': user.generate_auth_token(False).decode('ascii')})
    return jsonify({"status": 201,"success":True,"data":{"userid":user.id,"useremail":user.email,"userrole":rols.name,"token":user.generate_auth_token(False).decode('ascii'),"userroleid":userroles.role_id,"isactive":user.active,"firstname":user.first_name}
})


