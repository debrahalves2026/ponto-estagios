import os
import re
import sqlite3
import tempfile
from contextlib import contextmanager
from functools import wraps
from flask import session, redirect, after_this_request, g
from werkzeug.utils import secure_filename
from . import config as app_config
from database.conexao import conectar


def get_db_connection():
    if not hasattr(g, 'db_conn'):
        g.db_conn = conectar()
        g.db_conn.row_factory = sqlite3.Row
    return g.db_conn


def close_db_connection(exception=None):
    conn = getattr(g, 'db_conn', None)
    if conn is not None:
        conn.close()


@contextmanager
def db_cursor(commit=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception:
        if commit:
            conn.rollback()
        raise


def query_one(query, params=()):
    conn = get_db_connection()
    cursor = conn.execute(query, params)
    return cursor.fetchone()


def query_all(query, params=()):
    conn = get_db_connection()
    cursor = conn.execute(query, params)
    return cursor.fetchall()


def execute_query(query, params=()):
    conn = get_db_connection()
    cursor = conn.execute(query, params)
    conn.commit()
    return cursor


def execute_many(query, params_list):
    conn = get_db_connection()
    cursor = conn.executemany(query, params_list)
    conn.commit()
    return cursor


def ensure_upload_folder():
    os.makedirs(app_config.UPLOAD_FOLDER, exist_ok=True)
    return app_config.UPLOAD_FOLDER


def safe_filename(value):
    return secure_filename(value)


def save_temp_file(suffix):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_path = temp_file.name
    temp_file.close()
    return temp_path


def clean_temp_file(path):
    @after_this_request
    def remove_file(response):
        try:
            os.remove(path)
        except OSError:
            pass
        return response
    return remove_file


def validate_password(password):
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'
    return bool(re.match(pattern, password))


def login_required(role):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if role == 'administrador' and 'administrador_id' not in session:
                return redirect('/login-administrador')
            if role == 'gestor' and 'gestor_id' not in session:
                return redirect('/login-gestor-nucleo')
            if role == 'colaborador' and 'colaborador_id' not in session:
                return redirect('/login-colaborador')
            if role == 'any' and not any(k in session for k in ('administrador_id', 'gestor_id', 'colaborador_id')):
                return redirect('/login-colaborador')
            return view(*args, **kwargs)
        return wrapped
    return decorator


def validate_pdf_upload(file):
    if not file:
        return False, 'Nenhum arquivo enviado.'
    if not file.filename.lower().endswith('.pdf'):
        return False, 'Apenas arquivos PDF são permitidos.'
    return True, ''
