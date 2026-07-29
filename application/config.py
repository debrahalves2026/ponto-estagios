import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))


def _first_non_empty(*values):
	for value in values:
		if value and value.strip():
			return value.strip()
	return ''


def _resolve_database_path():
	# Explicit env vars always win.
	explicit_path = _first_non_empty(
		os.environ.get('DATABASE_PATH', ''),
		os.environ.get('SQLITE_DB_PATH', '')
	)
	if explicit_path:
		return explicit_path

	# Render persistent disk path when configured.
	render_disk_path = _first_non_empty(os.environ.get('RENDER_DISK_PATH', ''))
	if render_disk_path:
		return os.path.join(render_disk_path, 'ponto.db')

	# Common default mount point for persistent disks on Render.
	if os.environ.get('RENDER', '').strip() and os.path.isdir('/var/data'):
		return '/var/data/ponto.db'

	# Local development fallback.
	return os.path.join(PROJECT_ROOT, 'ponto.db')


DATABASE_PATH = _resolve_database_path()

# Warn when production-like environment uses a local project path.
_abs_project_root = os.path.abspath(PROJECT_ROOT)
_abs_database_path = os.path.abspath(DATABASE_PATH)
IS_EPHEMERAL_DB_RISK = (
	bool(os.environ.get('RENDER', '').strip() or os.environ.get('DYNO', '').strip())
	and _abs_database_path.startswith(_abs_project_root)
)

UPLOAD_FOLDER = os.environ.get(
	'UPLOAD_FOLDER',
	os.path.join(PROJECT_ROOT, 'uploads', 'folhas_assinadas')
)
SECRET_KEY = os.environ.get('SECRET_KEY', 'ponto_web_2026')

# PostgreSQL / Supabase
DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()
