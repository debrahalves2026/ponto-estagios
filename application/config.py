import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'ponto.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'folhas_assinadas')
SECRET_KEY = os.environ.get('SECRET_KEY', 'ponto_web_2026')
