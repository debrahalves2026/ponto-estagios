import sqlite3
import os

try:
    from application import config as app_config
except ModuleNotFoundError:
    # Permite executar este arquivo diretamente a partir da pasta database.
    import sys

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from application import config as app_config


def conectar():
    caminho = os.path.abspath(app_config.DATABASE_PATH)
    pasta_banco = os.path.dirname(caminho)
    if pasta_banco:
        os.makedirs(pasta_banco, exist_ok=True)

    print("BANCO:", caminho)

    conn = sqlite3.connect(caminho, timeout=30.0, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


if __name__ == '__main__':
    conn = conectar()
    conn.close()
    print('Conexao com banco realizada com sucesso.')