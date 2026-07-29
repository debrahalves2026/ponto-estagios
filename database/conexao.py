import os
import psycopg2

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
    database_url = app_config.DATABASE_URL
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL nao configurada. "
            "Defina a variavel de ambiente DATABASE_URL com a string de conexao do PostgreSQL/Supabase."
        )
    print("BANCO: PostgreSQL (Supabase)")
    conn = psycopg2.connect(database_url)
    return conn


if __name__ == '__main__':
    conn = conectar()
    conn.close()
    print('Conexao com banco realizada com sucesso.')