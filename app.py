import os
from flask import Flask, redirect, url_for, render_template, jsonify
from flask_security import current_user
from forms import ExtRegisterForm
from extensions import user_db, user_datastore, security
import utils


# Blueprints
from api.api import api
from panel.panel import panel

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['ENPUBLIC_SECRET']
app.config['MONGODB_SETTINGS'] = {
    'host': os.environ['ENPUBLIC_MONGO_URL']
}
app.config['SECURITY_PASSWORD_SALT'] = os.environ['PASSWORD_SALT']
app.config['SECURITY_POST_LOGIN_VIEW'] = '/panel'
app.config['SECURITY_UNAUTHORIZED_VIEW'] = '/'
app.config['SECURITY_POST_CHANGE_VIEW'] = '/'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_CHANGEABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SECURITY_SEND_PASSWORD_CHANGE_EMAIL'] = False
app.config['SECURITY_SEND_PASSWORD_RESET_EMAIL'] = False
app.config['SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL'] = False

app.register_blueprint(api)
app.register_blueprint(panel)


user_db.init_app(app)
security.init_app(app, user_datastore, register_form=ExtRegisterForm)


@app.before_first_request
def create_system():
    # Create first user
    utils.create_admin_user()

    # Create Neo database
    utils.create_neo_db()

    # Create Achievements
    utils.create_achievements()


@app.errorhandler(401)
def unauthorized_access():
    return jsonify({'message': 'Unauthorized access, you need an account to access.'}), 401


@app.route('/', methods=['GET'])
def main():
    if current_user.has_role('admin'):
        return redirect(url_for('panel.panel_main'))
    else:
        return render_template("index.html")


if __name__ == '__main__':
    debug = False
    try:
        debug_env = os.environ['ENPUBLIC_DEBUG']
        if debug_env == '1':
            debug = True
    except KeyError:
        debug = False

    app.run(host='0.0.0.0', debug=debug)
