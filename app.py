# START THIS FILE TO RUN THE WEBSITE
# Use: python app.py

from flask import Flask
from application import config as app_config
from database.models import criar_tabelas
from application.app_utils import close_db_connection
from application.routes import main_bp

app = Flask(__name__)
app.config.from_object(app_config)
app.secret_key = app_config.SECRET_KEY
app.teardown_appcontext(close_db_connection)
app.register_blueprint(main_bp)

criar_tabelas()

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, threaded=True)
