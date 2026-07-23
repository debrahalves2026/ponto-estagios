import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))

render_disk_path = os.environ.get('RENDER_DISK_PATH', '').strip()
if render_disk_path:
	DATABASE_PATH = os.path.join(render_disk_path, 'ponto.db')
else:
	DATABASE_PATH = os.environ.get(
		'SQLITE_DB_PATH',
		os.path.join(PROJECT_ROOT, 'ponto.db')
	)

UPLOAD_FOLDER = os.environ.get(
	'UPLOAD_FOLDER',
	os.path.join(PROJECT_ROOT, 'uploads', 'folhas_assinadas')
)
SECRET_KEY = os.environ.get('SECRET_KEY', 'ponto_web_2026')
