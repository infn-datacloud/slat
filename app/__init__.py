# Copyright (c) Istituto Nazionale di Fisica Nucleare (INFN). 2020-2024
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
from flask import Flask, json, render_template, flash, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from app.extensions import cmdb_client, flaat
from flask_migrate import upgrade
from .models import migrate, db, login_manager
from flask_dance.consumer import oauth_authorized
from app.auth import indigoiam
from app.auth import egicheckin
from flask_login import login_required, logout_user


def to_json(obj):
    return json.dumps(obj, separators=(',', ': '))


def create_app(config_class='config.default'):
    app = Flask(__name__, instance_relative_config=True)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.secret_key = "30bb7cf2-1fef-4d26-83f0-8096b6dcc7a3"
    app.config.from_object(config_class)
    app.config.from_file('config.json', load=json.load)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    flaat.init_app(app)
    cmdb_client.init_app(app)
    
    
    # Register blueprints
    register_blueprints(app)
    
    # Setup Flaat and other configurations
    setup_auth(app)
    setup_logging(app)
    
    # Run database migrations
    with app.app_context():
        upgrade(directory="migrations", revision="head")

    # Set custom Jinja filters
    app.jinja_env.filters['to_json'] = to_json
    
    return app

def setup_auth(app):
    with app.app_context():
    
        iam_blueprint = indigoiam.create_blueprint()
        app.register_blueprint(iam_blueprint, url_prefix="/login")

        # create/login local user on successful OAuth login
        @oauth_authorized.connect_via(iam_blueprint)
        def iam_logged_in(blueprint, token):
            return indigoiam.auth_blueprint_login(blueprint, token)


        if app.config.get('EGI_AAI_CLIENT_ID') and app.config.get('EGI_AAI_CLIENT_SECRET'):
            egicheckin_blueprint = egicheckin.create_blueprint()
            app.register_blueprint(egicheckin_blueprint, url_prefix="/login")


            @oauth_authorized.connect_via(egicheckin_blueprint)
            def egicheckin_logged_in(blueprint, token):
                return egicheckin.auth_blueprint_login(blueprint, token)

            # Inject the variable inject_egi_aai_enabled automatically into the context of templates
            @app.context_processor
            def inject_egi_aai_enabled():
                return dict(is_egi_aai_enabled=True)

        flaat.set_trusted_OP_list([idp['iss'] for idp in app.config.get('TRUSTED_OIDC_IDP_LIST', [])])
        flaat.set_request_timeout(20)

def setup_logging(app):
    loglevel = app.config.get("LOG_LEVEL", "INFO")
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {loglevel}')
    logging.basicConfig(level=numeric_level)

def register_blueprints(app):

    @app.route('/')
    def login():
        return render_template('home.html')


    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You have logged out", 'success')
        return redirect(url_for("login"))

    from app.rest.routes import rest_bp
    from app.sla.routes import sla_bp
    from app.group.routes import group_bp
    from app.provider.routes import provider_bp

    app.register_blueprint(rest_bp, url_prefix="/rest")
    app.register_blueprint(sla_bp, url_prefix="/sla")
    app.register_blueprint(group_bp, url_prefix="/group")
    app.register_blueprint(provider_bp, url_prefix="/provider")
