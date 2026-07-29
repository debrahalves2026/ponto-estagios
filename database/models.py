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

    conn.commit()
    conn.close()