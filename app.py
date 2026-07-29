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

if getattr(app_config, 'IS_EPHEMERAL_DB_RISK', False):
    print(
        'ALERTA: DATABASE_PATH aponta para a pasta do projeto em ambiente de deploy. '
        'Configure SQLITE_DB_PATH ou RENDER_DISK_PATH para um disco persistente.'
    )

criar_tabelas()

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, threaded=True)
