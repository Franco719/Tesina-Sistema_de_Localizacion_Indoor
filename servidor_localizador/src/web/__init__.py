from flask import Flask
from flask_session import Session
from flask_cors import CORS
#from src.core.bcrypt import Bcrypt
from src.web import routes
#from src.web.handlers.auth import is_authenticated
#from src.web.handlers.auth import is_system_admin
#from src.web.handlers.auth import check_permission
#from src.web.handlers import error
from src.core import database
#from src.core import seeds
from src.core.config import config
from flask import render_template
#from web.controllers.teams.handlers.error import styled_error
#from web.controllers.payments.handlers.style_date import style as style_date
#from src.web.upload import storage
import locale
"""from src.web.controllers.teams.handlers.files.sytle_file_names import (
    style as style_file_name,
)"""
#from src.web.controllers.auth import configure_oauth

def create_app(env="development", static_folder="../../static"):
    app = Flask(__name__, static_folder=static_folder)

    # Carga la configuración de la app
    app.config.from_object(config[env])

    # Configura OAuth para Google
    #configure_oauth(app)

    # Register routes
    routes.register(app)

    # Initialize the storage
    #storage.init_app(app)

    # Initialize the database
    database.init_app(app)

    # enable CORS
    CORS(app)

    # Register errors
    #app.register_error_handler(404, error.not_found_error)
    #app.register_error_handler(401, error.unauthorized)

    # Register functions on jinja
    #app.jinja_env.globals.update(is_authenticated=is_authenticated)
    #app.jinja_env.globals.update(is_system_admin=is_system_admin)
    #app.jinja_env.globals.update(check_permission=check_permission)
    #app.jinja_env.globals.update(styled=styled_error)
    #app.jinja_env.globals.update(style_date=style_date)
    #app.jinja_env.globals.update(style_file=style_file_name)

    # Commands for the database
    @app.cli.command(name="reset-db")
    def reset():
        database.reset_db()

    #@app.cli.command(name="seed-db")
    #def seed():
    #    seeds.seed_db()

    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

    return app