#!/usr/bin/env python
import os
from flask import Flask, abort, request, jsonify, g, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
import datetime
from flask import Flask, request, render_template_string,abort, jsonify, g, url_for
from flask_babelex import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_user import current_user, login_required, roles_required, UserManager, UserMixin





# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'The super secret key CHANGE IN PRODUCTION'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/db_name'
##Can change the library instead of pymysql and instead of local host you can input any ##production RDBMS.
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['USER_EMAIL_SENDER_EMAIL'] = "yourmailid@domain.com"


auth = HTTPBasicAuth()

from __init__ import db

# models
from user_models.user import User


# controllers
from controllers.user_controller import user_controller


# routes
app.register_blueprint(user_controller)


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.email})


if __name__ == '__main__':
    db.create_all()    
    app.run(host='0.0.0.0', debug=True)
