from database.conexao import conectar

def criar_tabelas():

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS colaboradores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        vinculo TEXT,
        nucleo TEXT,
        turno TEXT,
        horario TEXT,
        presencial TEXT,
        unidade_exercicio TEXT,
        procurador_monitor TEXT,
        celular TEXT,
        login TEXT,
        senha TEXT,
        status TEXT DEFAULT 'Ativo',
        cancel_observacao TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gestores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        nucleo TEXT,
        unidade_exercicio TEXT,
        celular TEXT,
        login TEXT UNIQUE,
        senha TEXT,
        status TEXT DEFAULT 'Ativo',
        cancel_observacao TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS registros_ponto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        colaborador_id INTEGER,
        data TEXT,
        entrada TEXT,
        saida_final TEXT,
        observacao TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ajustes_ponto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        colaborador_id INTEGER,
        data TEXT,
        tipo_ajuste TEXT,
        horario_correto TEXT,
        motivo TEXT,
        status TEXT DEFAULT 'Pendente',
        motivo_reprovacao TEXT,
        analisado_por TEXT,
        data_analise TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS eventos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT,
        tipo TEXT,
        data TEXT,
        descricao TEXT,
        nucleo TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs_sistema (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_hora TEXT NOT NULL,
        tipo_usuario TEXT,
        nome_usuario TEXT,
        acao TEXT NOT NULL,
        detalhes TEXT
    )
    """)

    cursor.execute("PRAGMA table_info(colaboradores)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'cancel_observacao' not in columns:
        cursor.execute("ALTER TABLE colaboradores ADD COLUMN cancel_observacao TEXT")
    if 'folha_assinada_path' not in columns:
        cursor.execute("ALTER TABLE colaboradores ADD COLUMN folha_assinada_path TEXT")
    if 'folha_assinada_nome' not in columns:
        cursor.execute("ALTER TABLE colaboradores ADD COLUMN folha_assinada_nome TEXT")

    cursor.execute("PRAGMA table_info(gestores)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'cancel_observacao' not in columns:
        cursor.execute("ALTER TABLE gestores ADD COLUMN cancel_observacao TEXT")

    cursor.execute("PRAGMA table_info(ajustes_ponto)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'tipo_ajuste' not in columns:
        cursor.execute("ALTER TABLE ajustes_ponto ADD COLUMN tipo_ajuste TEXT")
    if 'horario_correto' not in columns:
        cursor.execute("ALTER TABLE ajustes_ponto ADD COLUMN horario_correto TEXT")
    if 'motivo_reprovacao' not in columns:
        cursor.execute("ALTER TABLE ajustes_ponto ADD COLUMN motivo_reprovacao TEXT")
    if 'analisado_por' not in columns:
        cursor.execute("ALTER TABLE ajustes_ponto ADD COLUMN analisado_por TEXT")
    if 'data_analise' not in columns:
        cursor.execute("ALTER TABLE ajustes_ponto ADD COLUMN data_analise TEXT")

    conn.commit()

    conn.close()