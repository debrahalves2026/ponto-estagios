from database.conexao import conectar


def _adicionar_coluna_se_ausente(cursor, tabela, coluna, tipo):
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = %s AND column_name = %s
    """, (tabela, coluna))
    if not cursor.fetchone():
        cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {tipo}")


def criar_tabelas():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS colaboradores (
        id SERIAL PRIMARY KEY,
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
        id SERIAL PRIMARY KEY,
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
        id SERIAL PRIMARY KEY,
        colaborador_id INTEGER,
        data TEXT,
        entrada TEXT,
        saida_final TEXT,
        observacao TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ajustes_ponto (
        id SERIAL PRIMARY KEY,
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
        id SERIAL PRIMARY KEY,
        titulo TEXT,
        tipo TEXT,
        data TEXT,
        descricao TEXT,
        nucleo TEXT,
        horario TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs_sistema (
        id SERIAL PRIMARY KEY,
        data_hora TEXT NOT NULL,
        tipo_usuario TEXT,
        nome_usuario TEXT,
        acao TEXT NOT NULL,
        detalhes TEXT
    )
    """)

    # Migracoes: adiciona colunas que podem nao existir em bancos ja criados
    # Colunas de status críticas
    _adicionar_coluna_se_ausente(cursor, 'colaboradores', 'status', 'TEXT DEFAULT \'Ativo\'')
    _adicionar_coluna_se_ausente(cursor, 'gestores', 'status', 'TEXT DEFAULT \'Ativo\'')
    _adicionar_coluna_se_ausente(cursor, 'ajustes_ponto', 'status', 'TEXT DEFAULT \'Pendente\'')
    
    # Outras colunas de migração
    _adicionar_coluna_se_ausente(cursor, 'colaboradores', 'cancel_observacao', 'TEXT')
    _adicionar_coluna_se_ausente(cursor, 'colaboradores', 'folha_assinada_path', 'TEXT')
    _adicionar_coluna_se_ausente(cursor, 'colaboradores', 'folha_assinada_nome', 'TEXT')
    _adicionar_coluna_se_ausente(cursor, 'gestores', 'cancel_observacao', 'TEXT')
    _adicionar_coluna_se_ausente(cursor, 'ajustes_ponto', 'tipo_ajuste', 'TEXT')
    _adicionar_coluna_se_ausente(cursor, 'ajustes_ponto', 'horario_correto', 'TEXT')
    _adicionar_coluna_se_ausente(cursor, 'ajustes_ponto', 'motivo_reprovacao', 'TEXT')
    _adicionar_coluna_se_ausente(cursor, 'ajustes_ponto', 'analisado_por', 'TEXT')
    _adicionar_coluna_se_ausente(cursor, 'ajustes_ponto', 'data_analise', 'TEXT')
    _adicionar_coluna_se_ausente(cursor, 'eventos', 'horario', 'TEXT')

    # Índices para melhor performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_colaboradores_status
        ON colaboradores (status)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_colaboradores_login
        ON colaboradores (login)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_colaboradores_nucleo
        ON colaboradores (nucleo)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_gestores_login
        ON gestores (login)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_registros_colaborador_id
        ON registros_ponto (colaborador_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_registros_data
        ON registros_ponto (data)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_ajustes_colaborador_id
        ON ajustes_ponto (colaborador_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_ajustes_status
        ON ajustes_ponto (status)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_eventos_data
        ON eventos (data)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_eventos_nucleo
        ON eventos (nucleo)
    """)

    conn.commit()
    conn.close()