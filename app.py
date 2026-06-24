from flask import Flask, render_template, request, redirect, session, send_file
from database.models import criar_tabelas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from openpyxl import Workbook
from database.conexao import conectar
from datetime import datetime
from zoneinfo import ZoneInfo
import re

app = Flask(__name__)

app.secret_key = "ponto_web_2026"

criar_tabelas()

@app.route('/')
def inicio():
    return render_template('index.html')


# =========================
# ADMINISTRADOR
# =========================

@app.route('/login-administrador', methods=['GET', 'POST'])
def login_administrador():

    if request.method == 'POST':

        login = request.form.get('login')
        senha = request.form.get('senha')

        if login == 'gestor1' and senha == 'gestor2026':
            return redirect('/dashboard-administrador')

        return render_template(
            'administrador/login_administrador.html',
            erro='Login ou senha inválidos'
        )

    return render_template(
        'administrador/login_administrador.html'
    )


# =========================
# GESTOR DO NÚCLEO
# =========================

@app.route('/login-gestor-nucleo', methods=['GET', 'POST'])
def login_gestor_nucleo():

    if request.method == 'POST':

        login = request.form.get('login')
        senha = request.form.get('senha')

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM gestores
            WHERE login = ?
            AND senha = ?
            AND status = 'Ativo'
        """, (
            login,
            senha
        ))

        gestor = cursor.fetchone()

        conn.close()

        if gestor:

            session['gestor_id'] = gestor[0]
            session['nome_gestor'] = gestor[1]
            session['nucleo_gestor'] = gestor[2]

            # Primeiro acesso
            if gestor[6] == "Novocolab123":
                return redirect('/primeiro-acesso-gestor')

            return redirect('/dashboard-gestor-nucleo')

        return render_template(
            'gestor_nucleo/login_gestor_nucleo.html',
            erro='Login ou senha inválidos'
        )

    return render_template(
        'gestor_nucleo/login_gestor_nucleo.html'
    )


@app.route('/dashboard-gestor-nucleo')
def dashboard_gestor_nucleo():

    if 'gestor_id' not in session:
        return redirect('/login-gestor-nucleo')

    conn = conectar()
    cursor = conn.cursor()

    # Total de colaboradores
    cursor.execute("""
        SELECT COUNT(*)
        FROM colaboradores
        WHERE nucleo = ?
    """, (
        session['nucleo_gestor'],
    ))
    total_colaboradores = cursor.fetchone()[0]

    # Colaboradores ativos
    cursor.execute("""
        SELECT COUNT(*)
        FROM colaboradores
        WHERE nucleo = ?
        AND status = 'Ativo'
    """, (
        session['nucleo_gestor'],
    ))
    colaboradores_ativos = cursor.fetchone()[0]

    # Colaboradores inativos
    cursor.execute("""
        SELECT COUNT(*)
        FROM colaboradores
        WHERE nucleo = ?
        AND status = 'Inativo'
    """, (
        session['nucleo_gestor'],
    ))
    colaboradores_inativos = cursor.fetchone()[0]

    # Ajustes pendentes
    cursor.execute("""
        SELECT COUNT(*)
        FROM ajustes_ponto
        INNER JOIN colaboradores
        ON ajustes_ponto.colaborador_id = colaboradores.id
        WHERE colaboradores.nucleo = ?
        AND ajustes_ponto.status = 'Pendente'
    """, (
        session['nucleo_gestor'],
    ))
    ajustes_pendentes = cursor.fetchone()[0]

    conn.close()

    return render_template(
        'gestor_nucleo/dashboard_gestor_nucleo.html',
        nome=session['nome_gestor'],
        nucleo=session['nucleo_gestor'],
        total_colaboradores=total_colaboradores,
        colaboradores_ativos=colaboradores_ativos,
        colaboradores_inativos=colaboradores_inativos,
        ajustes_pendentes=ajustes_pendentes
    )


# =========================
# CADASTRO DE GESTOR
# =========================

@app.route('/cadastro-gestor')
def cadastro_gestor():

    return render_template(
        'administrador/cadastro_gestor.html'
    )


@app.route('/salvar-gestor', methods=['POST'])
def salvar_gestor():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO gestores (
            nome,
            nucleo,
            unidade_exercicio,
            celular,
            login,
            senha
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        request.form['nome'],
        request.form['nucleo'],
        request.form['unidade_exercicio'],
        request.form['celular'],
        request.form['login'],
        "Novocolab123"
    ))

    conn.commit()
    conn.close()

    return redirect('/gestores-cadastrados')

# =========================
# GESTORES CADASTRADOS
# =========================

@app.route('/editar-gestor/<int:id>')
def editar_gestor(id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM gestores
        WHERE id = ?
    """, (
        id,
    ))

    gestor = cursor.fetchone()

    conn.close()

    return render_template(
        'administrador/editar_gestor.html',
        gestor=gestor
    )


@app.route('/atualizar-gestor/<int:id>', methods=['POST'])
def atualizar_gestor(id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE gestores
        SET
            nome = ?,
            nucleo = ?,
            login = ?
        WHERE id = ?
    """, (
        request.form['nome'],
        request.form['nucleo'],
        request.form['login'],
        id
    ))

    conn.commit()
    conn.close()

    return redirect('/gestores-cadastrados')


@app.route('/cancelar-gestor/<int:id>')
def cancelar_gestor(id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE gestores
        SET status = 'Inativo'
        WHERE id = ?
    """, (
        id,
    ))

    conn.commit()
    conn.close()

    return redirect('/gestores-cadastrados')

@app.route('/resetar-senha-gestor/<int:id>')
def resetar_senha_gestor(id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE gestores
        SET senha = ?
        WHERE id = ?
    """, (
        "Novocolab123",
        id
    ))

    conn.commit()
    conn.close()

    return redirect('/gestores-cadastrados')

@app.route('/gestores-cadastrados')
def gestores_cadastrados():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM gestores
        ORDER BY nome
    """)

    gestores = cursor.fetchall()

    conn.close()

    return render_template(
        'administrador/gestores_cadastrados.html',
        gestores=gestores
    )


# =========================
# COLABORADOR
# =========================

@app.route('/login-colaborador', methods=['GET', 'POST'])
def login_colaborador():

    if request.method == 'POST':

        login = request.form.get('login')
        senha = request.form.get('senha')

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM colaboradores
            WHERE login = ?
            AND senha = ?
            AND status = 'Ativo'
        """, (
            login,
            senha
        ))

        colaborador = cursor.fetchone()

        conn.close()

        if colaborador:

            session['colaborador_id'] = colaborador[0]
            session['nome'] = colaborador[1]

            if colaborador[11] == "Novocolab123":
                return redirect('/primeiro-acesso')

            return redirect('/ponto')

        return render_template(
            'colaborador/login_colaborador.html',
            erro='Login ou senha inválidos'
        )

    return render_template(
        'colaborador/login_colaborador.html'
    )


# =========================
# CADASTRO DE COLABORADOR
# =========================

@app.route('/cadastro-colaborador')
def cadastro_colaborador():

    return render_template(
        'administrador/cadastro_colaborador.html'
    )


# =========================
# DASHBOARD ADMINISTRADOR
# =========================

@app.route('/dashboard-administrador')
def dashboard_administrador():

    conn = conectar()
    cursor = conn.cursor()

    # Total de colaboradores
    cursor.execute("""
        SELECT COUNT(*)
        FROM colaboradores
    """)
    total_colaboradores = cursor.fetchone()[0]

    # Colaboradores ativos
    cursor.execute("""
        SELECT COUNT(*)
        FROM colaboradores
        WHERE status = 'Ativo'
    """)
    colaboradores_ativos = cursor.fetchone()[0]

    # Colaboradores inativos
    cursor.execute("""
        SELECT COUNT(*)
        FROM colaboradores
        WHERE status = 'Inativo'
    """)
    colaboradores_inativos = cursor.fetchone()[0]

    # Total de gestores
    cursor.execute("""
        SELECT COUNT(*)
        FROM gestores
        WHERE status = 'Ativo'
    """)
    total_gestores = cursor.fetchone()[0]

    # Total de núcleos
    cursor.execute("""
        SELECT COUNT(DISTINCT nucleo)
        FROM colaboradores
    """)
    total_nucleos = cursor.fetchone()[0]

    # Ajustes pendentes
    cursor.execute("""
        SELECT COUNT(*)
        FROM ajustes_ponto
        WHERE status = 'Pendente'
    """)
    ajustes_pendentes = cursor.fetchone()[0]

    conn.close()

    return render_template(
        'administrador/dashboard_administrador.html',
        total_colaboradores=total_colaboradores,
        colaboradores_ativos=colaboradores_ativos,
        colaboradores_inativos=colaboradores_inativos,
        total_gestores=total_gestores,
        total_nucleos=total_nucleos,
        ajustes_pendentes=ajustes_pendentes
    )

# =========================
# COLABORADORES CADASTRADOS
# =========================

@app.route('/colaboradores-cadastrados')
def colaboradores_cadastrados():

    conn = conectar()
    cursor = conn.cursor()

    # Administrador vê todos os colaboradores
    if 'gestor_id' not in session:

        cursor.execute("""
            SELECT *
            FROM colaboradores
            ORDER BY nome
        """)

    # Gestor do Núcleo vê somente os colaboradores do seu núcleo
    else:

        cursor.execute("""
            SELECT *
            FROM colaboradores
            WHERE nucleo = ?
            ORDER BY nome
        """, (
            session['nucleo_gestor'],
        ))

    colaboradores = cursor.fetchall()

    conn.close()

    return render_template(
        'administrador/colaboradores.html',
        colaboradores=colaboradores
    )


# =========================
# PONTO
# =========================

@app.route('/ponto')
def ponto():

    if 'colaborador_id' not in session:
        return redirect('/login-colaborador')

    conn = conectar()
    cursor = conn.cursor()

    data_hoje = datetime.now(
        ZoneInfo("America/Sao_Paulo")
    ).strftime('%d/%m/%Y')

    cursor.execute("""
        SELECT
            entrada,
            saida_final
        FROM registros_ponto
        WHERE colaborador_id = ?
        AND data = ?
    """, (
        session['colaborador_id'],
        data_hoje
    ))

    registro = cursor.fetchone()

    conn.close()

    entrada = "--:--"
    saida_final = "--:--"

    if registro:
        entrada = registro[0] or "--:--"
        saida_final = registro[1] or "--:--"

    return render_template(
        'colaborador/ponto.html',
        nome=session['nome'],
        entrada=entrada,
        saida_final=saida_final
    )


# =========================
# AJUSTE DE PONTO
# =========================

@app.route('/ajuste-ponto')
def ajuste_ponto():

    return render_template(
        'colaborador/ajuste_ponto.html'
    )


# =========================
# SOLICITAÇÕES DE AJUSTE
# =========================

@app.route('/solicitacoes-ajuste')
def solicitacoes_ajuste():

    conn = conectar()
    cursor = conn.cursor()

    # Administrador vê todos
    if 'gestor_id' not in session:

        cursor.execute("""
            SELECT
                ajustes_ponto.id,
                colaboradores.nome,
                colaboradores.nucleo,
                ajustes_ponto.data,
                ajustes_ponto.motivo,
                ajustes_ponto.status
            FROM ajustes_ponto
            INNER JOIN colaboradores
            ON ajustes_ponto.colaborador_id = colaboradores.id
            ORDER BY ajustes_ponto.id DESC
        """)

    # Gestor do Núcleo vê apenas os ajustes do seu núcleo
    else:

        cursor.execute("""
            SELECT
                ajustes_ponto.id,
                colaboradores.nome,
                colaboradores.nucleo,
                ajustes_ponto.data,
                ajustes_ponto.motivo,
                ajustes_ponto.status
            FROM ajustes_ponto
            INNER JOIN colaboradores
            ON ajustes_ponto.colaborador_id = colaboradores.id
            WHERE colaboradores.nucleo = ?
            ORDER BY ajustes_ponto.id DESC
        """, (
            session['nucleo_gestor'],
        ))

    ajustes = cursor.fetchall()

    conn.close()

    return render_template(
        'administrador/solicitacoes_ajuste.html',
        ajustes=ajustes
    )

# =========================
# APROVAR AJUSTE
# =========================

@app.route('/aprovar-ajuste/<int:id>')
def aprovar_ajuste(id):

    conn = conectar()
    cursor = conn.cursor()

    # Segurança para Gestor do Núcleo
    if 'gestor_id' in session:

        cursor.execute("""
            SELECT ajustes_ponto.id
            FROM ajustes_ponto
            INNER JOIN colaboradores
            ON ajustes_ponto.colaborador_id = colaboradores.id
            WHERE ajustes_ponto.id = ?
            AND colaboradores.nucleo = ?
        """, (
            id,
            session['nucleo_gestor']
        ))

        permissao = cursor.fetchone()

        if not permissao:
            conn.close()
            return redirect('/solicitacoes-ajuste')

    cursor.execute("""
        UPDATE ajustes_ponto
        SET status = 'Aprovado'
        WHERE id = ?
    """, (id,))

    conn.commit()
    conn.close()

    return redirect('/solicitacoes-ajuste')


# =========================
# REPROVAR AJUSTE
# =========================

@app.route('/reprovar-ajuste/<int:id>')
def reprovar_ajuste(id):

    conn = conectar()
    cursor = conn.cursor()

    # Segurança para Gestor do Núcleo
    if 'gestor_id' in session:

        cursor.execute("""
            SELECT ajustes_ponto.id
            FROM ajustes_ponto
            INNER JOIN colaboradores
            ON ajustes_ponto.colaborador_id = colaboradores.id
            WHERE ajustes_ponto.id = ?
            AND colaboradores.nucleo = ?
        """, (
            id,
            session['nucleo_gestor']
        ))

        permissao = cursor.fetchone()

        if not permissao:
            conn.close()
            return redirect('/solicitacoes-ajuste')

    cursor.execute("""
        UPDATE ajustes_ponto
        SET status = 'Reprovado'
        WHERE id = ?
    """, (id,))

    conn.commit()
    conn.close()

    return redirect('/solicitacoes-ajuste')


# =========================
# MEUS AJUSTES
# =========================

@app.route('/meus-ajustes')
def meus_ajustes():

    if 'colaborador_id' not in session:
        return redirect('/login-colaborador')

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            data,
            motivo,
            status
        FROM ajustes_ponto
        WHERE colaborador_id = ?
        ORDER BY id DESC
    """, (
        session['colaborador_id'],
    ))

    ajustes = cursor.fetchall()

    conn.close()

    return render_template(
        'colaborador/meus_ajustes.html',
        ajustes=ajustes
    )


# =========================
# CALENDÁRIO
# =========================

@app.route('/calendario')
def calendario():

    return render_template(
        'administrador/calendario.html'
    )


# =========================
# RELATÓRIOS
# =========================

@app.route('/relatorios')
def relatorios():

    conn = conectar()
    cursor = conn.cursor()

    # Administrador vê todos
    if 'gestor_id' not in session:

        cursor.execute("""
            SELECT id, nome
            FROM colaboradores
            WHERE status = 'Ativo'
            ORDER BY nome
        """)

    # Gestor do Núcleo vê apenas o seu núcleo
    else:

        cursor.execute("""
            SELECT id, nome
            FROM colaboradores
            WHERE status = 'Ativo'
            AND nucleo = ?
            ORDER BY nome
        """, (
            session['nucleo_gestor'],
        ))

    colaboradores = cursor.fetchall()

    conn.close()

    return render_template(
        'administrador/relatorios.html',
        colaboradores=colaboradores,
        registros=None
    )


# =========================
# VISUALIZAR RELATÓRIO
# =========================

@app.route('/visualizar-relatorio', methods=['POST'])
def visualizar_relatorio():

    colaborador_id = request.form['colaborador_id']

    conn = conectar()
    cursor = conn.cursor()

    # Lista de colaboradores
    if 'gestor_id' not in session:

        cursor.execute("""
            SELECT id, nome
            FROM colaboradores
            WHERE status = 'Ativo'
            ORDER BY nome
        """)

    else:

        cursor.execute("""
            SELECT id, nome
            FROM colaboradores
            WHERE status = 'Ativo'
            AND nucleo = ?
            ORDER BY nome
        """, (
            session['nucleo_gestor'],
        ))

    colaboradores = cursor.fetchall()

    # Segurança adicional para Gestor do Núcleo
    if 'gestor_id' in session:

        cursor.execute("""
            SELECT id
            FROM colaboradores
            WHERE id = ?
            AND nucleo = ?
        """, (
            colaborador_id,
            session['nucleo_gestor']
        ))

        permissao = cursor.fetchone()

        if not permissao:

            conn.close()

            return render_template(
                'administrador/relatorios.html',
                colaboradores=colaboradores,
                registros=None,
                erro='Você não possui permissão para visualizar este colaborador.'
            )

    # Busca os registros
    cursor.execute("""
        SELECT
            data,
            entrada,
            saida_final
        FROM registros_ponto
        WHERE colaborador_id = ?
        ORDER BY id DESC
    """, (
        colaborador_id,
    ))

    registros = cursor.fetchall()

    cursor.execute("""
        SELECT nome
        FROM colaboradores
        WHERE id = ?
    """, (
        colaborador_id,
    ))

    nome_colaborador = cursor.fetchone()[0]

    conn.close()

    return render_template(
        'administrador/relatorios.html',
        colaboradores=colaboradores,
        registros=registros,
        nome_colaborador=nome_colaborador
    )

# =========================
# SALVAR COLABORADOR
# =========================

@app.route('/salvar-colaborador', methods=['POST'])
def salvar_colaborador():

    conn = conectar()
    cursor = conn.cursor()

    # Se for Gestor do Núcleo, usa automaticamente o núcleo dele
    if 'gestor_id' in session:
        nucleo = session['nucleo_gestor']

    # Se for Administrador, permite escolher o núcleo
    else:
        nucleo = request.form['nucleo']

    cursor.execute("""
        INSERT INTO colaboradores (
            nome,
            vinculo,
            nucleo,
            turno,
            horario,
            presencial,
            unidade_exercicio,
            procurador_monitor,
            celular,
            login,
            senha
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        request.form['nome'],
        request.form['vinculo'],
        nucleo,
        request.form['turno'],
        request.form['horario'],
        request.form['presencial'],
        request.form['unidade_exercicio'],
        request.form['procurador_monitor'],
        request.form['celular'],
        request.form['login'],
        request.form['senha']
    ))

    conn.commit()
    conn.close()

    return redirect('/colaboradores-cadastrados')


# =========================
# CANCELAR COLABORADOR
# =========================

@app.route('/cancelar-colaborador/<int:id>')
def cancelar_colaborador(id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE colaboradores
        SET status = 'Inativo'
        WHERE id = ?
    """, (
        id,
    ))

    conn.commit()
    conn.close()

    return redirect('/colaboradores-cadastrados')


# =========================
# EDITAR COLABORADOR
# =========================

@app.route('/editar-colaborador/<int:id>')
def editar_colaborador(id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM colaboradores
        WHERE id = ?
    """, (
        id,
    ))

    colaborador = cursor.fetchone()

    conn.close()

    return render_template(
        'administrador/editar_colaborador.html',
        colaborador=colaborador
    )


# =========================
# ATUALIZAR COLABORADOR
# =========================

@app.route('/atualizar-colaborador/<int:id>', methods=['POST'])
def atualizar_colaborador(id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE colaboradores
        SET
            nome = ?,
            nucleo = ?,
            turno = ?,
            horario = ?,
            celular = ?
        WHERE id = ?
    """, (
        request.form['nome'],
        request.form['nucleo'],
        request.form['turno'],
        request.form['horario'],
        request.form['celular'],
        id
    ))

    conn.commit()
    conn.close()

    return redirect('/colaboradores-cadastrados')


# =========================
# REGISTRAR ENTRADA
# =========================

@app.route('/registrar-entrada', methods=['POST'])
def registrar_entrada():

    if 'colaborador_id' not in session:
        return redirect('/login-colaborador')

    conn = conectar()
    cursor = conn.cursor()

    hora_atual = request.form['entrada']

    cursor.execute("""
        SELECT id
        FROM registros_ponto
        WHERE colaborador_id = ?
        AND data = ?
    """, (
        session['colaborador_id'],
        data_hoje
    ))

    registro = cursor.fetchone()

    if not registro:

        cursor.execute("""
            INSERT INTO registros_ponto (
                colaborador_id,
                data,
                entrada
            )
            VALUES (?, ?, ?)
        """, (
            session['colaborador_id'],
            data_hoje,
            hora_atual
        ))

        conn.commit()

    conn.close()

    return redirect('/ponto')


# =========================
# REGISTRAR SAÍDA FINAL
# =========================

@app.route('/registrar-saida-final', methods=['POST'])
def registrar_saida_final():

    if 'colaborador_id' not in session:
        return redirect('/login-colaborador')

    conn = conectar()
    cursor = conn.cursor()

    hora_atual = request.form['saida_final']

    cursor.execute("""
        UPDATE registros_ponto
        SET saida_final = ?
        WHERE colaborador_id = ?
        AND data = ?
    """, (
        hora_atual,
        session['colaborador_id'],
        data_hoje
    ))

    conn.commit()
    conn.close()

    return redirect('/ponto')

@app.route('/meu-relatorio')
def meu_relatorio():

    if 'colaborador_id' not in session:
        return redirect('/login-colaborador')

    from database.conexao import conectar

    conn = conectar()
    cursor = conn.cursor()

    mes_selecionado = request.args.get('mes')

    if mes_selecionado:

        ano = mes_selecionado.split('-')[0]
        mes = mes_selecionado.split('-')[1]

        cursor.execute("""
            SELECT
                data,
                entrada,
                saida_final,
                observacao
            FROM registros_ponto
            WHERE colaborador_id = ?
            AND substr(data,4,2) = ?
            AND substr(data,7,4) = ?
            ORDER BY id DESC
        """, (
            session['colaborador_id'],
            mes,
            ano
        ))

    else:

        cursor.execute("""
            SELECT
                data,
                entrada,
                saida_final,
                observacao
            FROM registros_ponto
            WHERE colaborador_id = ?
            ORDER BY id DESC
        """, (session['colaborador_id'],))

    registros = cursor.fetchall()

    conn.close()

    return render_template(
        'colaborador/meu_relatorio.html',
        registros=registros,
        nome=session['nome'],
        mes_selecionado=mes_selecionado
    )


@app.route('/salvar-observacao', methods=['POST'])
def salvar_observacao():

    if 'colaborador_id' not in session:
        return redirect('/login-colaborador')

    from database.conexao import conectar
    from datetime import datetime

    conn = conectar()
    cursor = conn.cursor()

    data = request.form['data']
    observacao = request.form['observacao']

    data_convertida = datetime.strptime(
        data,
        "%Y-%m-%d"
    ).strftime("%d/%m/%Y")

    cursor.execute("""
        UPDATE registros_ponto
        SET observacao = ?
        WHERE colaborador_id = ?
        AND data = ?
    """, (
        observacao,
        session['colaborador_id'],
        data_convertida
    ))

    conn.commit()
    conn.close()

    return redirect('/meu-relatorio')

from flask import send_file
from reportlab.pdfgen import canvas

@app.route('/gerar-pdf')
def gerar_pdf():

    if 'colaborador_id' not in session:
        return redirect('/login-colaborador')

    from database.conexao import conectar

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            nome,
            nucleo,
            horario
        FROM colaboradores
        WHERE id = ?
    """, (session['colaborador_id'],))

    colaborador = cursor.fetchone()

    mes_selecionado = request.args.get('mes')

    print("MES PDF:", mes_selecionado)

    cursor.execute("""
        SELECT
            data,
            entrada,
            saida_final,
            observacao
        FROM registros_ponto
        WHERE colaborador_id = ?
        ORDER BY data
    """, (session['colaborador_id'],))

    registros = cursor.fetchall()

    conn.close()

    nome_colaborador = colaborador[0].replace(" ", "_")

    if mes_selecionado and "-" in mes_selecionado:

        ano = mes_selecionado.split('-')[0]
        mes = mes_selecionado.split('-')[1]

        arquivo = f"Folha_Frequencia_{nome_colaborador}_{mes}_{ano}.pdf"

    else:

        arquivo = f"Folha_Frequencia_{nome_colaborador}.pdf"

    doc = SimpleDocTemplate(arquivo)

    estilos = getSampleStyleSheet()

    elementos = []

    elementos.append(
        Paragraph(
            "<b>FOLHA DE FREQUÊNCIA</b>",
            estilos['Title']
        )
    )

    if mes_selecionado:

        elementos.append(
            Paragraph(
                f"<b>Competência:</b> {mes}/{ano}",
                estilos['Normal']
            )
        )

        elementos.append(Spacer(1, 12))

    elementos.append(
        Paragraph(
            f"<b>Nome:</b> {colaborador[0]}",
            estilos['Normal']
        )
    )

    elementos.append(
        Paragraph(
            f"<b>Núcleo:</b> {colaborador[1]}",
            estilos['Normal']
        )
    )

    elementos.append(
        Paragraph(
            f"<b>Horário:</b> {colaborador[2]}",
            estilos['Normal']
        )
    )

    elementos.append(Spacer(1, 20))

    dados = [
        ["Data", "Entrada", "Saída", "Observação"]
    ]

    for registro in registros:

        dados.append([
            registro[0],
            registro[1] or "",
            registro[2] or "",
            registro[3] or ""
        ])

    tabela = Table(dados)

    tabela.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
    ]))

    elementos.append(tabela)

    elementos.append(Spacer(1, 120))

    elementos.append(
    Paragraph(
        "<b>VISTO</b>",
        estilos['Title']
    )
)

    elementos.append(Spacer(1, 50))

    assinaturas = Table([
    [
        "__________________________________",
        "__________________________________"
    ],
    [
        colaborador[0],
        "ASSINATURA/CARIMBO"
    ],
    [
        "Assinatura do Colaborador",
        "PROCURADOR DO ESTADO"
    ]
], colWidths=[250, 250])
    
    assinaturas.setStyle(TableStyle([
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
    ('BOTTOMPADDING', (0,0), (-1,-1), 8),
]))

    elementos.append(assinaturas)

    doc.build(elementos)

    return send_file(
        arquivo,
        as_attachment=True
    )

@app.route('/gerar-excel')
def gerar_excel():

    if 'colaborador_id' not in session:
        return redirect('/login-colaborador')

    from database.conexao import conectar

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            nome,
            nucleo,
            horario
        FROM colaboradores
        WHERE id = ?
    """, (session['colaborador_id'],))

    colaborador = cursor.fetchone()

    mes_selecionado = request.args.get('mes')

    print("MES PDF:", mes_selecionado)

    cursor.execute("""
        SELECT
            data,
            entrada,
            saida_final,
            observacao
        FROM registros_ponto
        WHERE colaborador_id = ?
        ORDER BY data
    """, (session['colaborador_id'],))

    registros = cursor.fetchall()

    conn.close()

    wb = Workbook()

    ws = wb.active

    ws.title = "Frequência"

    ws['A1'] = "FOLHA DE FREQUÊNCIA"

    if mes_selecionado and "-" in mes_selecionado:

        ano = mes_selecionado.split('-')[0]
        mes = mes_selecionado.split('-')[1]

        ws['A2'] = f"Competência: {mes}/{ano}"

    ws['A3'] = "Nome"
    ws['B3'] = colaborador[0]

    ws['A4'] = "Núcleo"
    ws['B4'] = colaborador[1]

    ws['A5'] = "Horário"
    ws['B5'] = colaborador[2]

    ws.append([])

    ws.append([
        "Data",
        "Entrada",
        "Saída",
        "Observação"
    ])

    for registro in registros:

        ws.append([
            registro[0],
            registro[1] or "",
            registro[2] or "",
            registro[3] or ""
        ])

    nome_colaborador = colaborador[0].replace(" ", "_")

    if mes_selecionado:

        arquivo = f"Folha_Frequencia_{nome_colaborador}_{mes}_{ano}.xlsx"

    else:

        arquivo = f"Folha_Frequencia_{nome_colaborador}.xlsx"

    wb.save(arquivo)

    return send_file(
        arquivo,
        as_attachment=True
    )

@app.route('/primeiro-acesso')
def primeiro_acesso():

    if 'colaborador_id' not in session:
        return redirect('/login-colaborador')

    return render_template(
    'colaborador/primeiro_acesso.html'
)

@app.route('/alterar-senha', methods=['POST'])
def alterar_senha():

    if 'colaborador_id' not in session:
        return redirect('/login-colaborador')

    senha1 = request.form['senha']
    senha2 = request.form['confirmar_senha']

    if senha1 != senha2:
        return """
        As senhas não coincidem.
        """

    if senha1 == "Novocolab123":
        return """
        A senha padrão não pode ser utilizada novamente.
        """

    padrao = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'

    if not re.match(padrao, senha1):

        return """
        A senha deve possuir:

        - mínimo de 8 caracteres;
        - uma letra maiúscula;
        - uma letra minúscula;
        - um número;
        - um caractere especial.
        """

    from database.conexao import conectar

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE colaboradores
        SET senha = ?
        WHERE id = ?
    """, (
        senha1,
        session['colaborador_id']
    ))

    conn.commit()
    conn.close()

    return redirect('/ponto')

@app.route('/lancar-ponto')
def lancar_ponto():

    if 'administrador_id' not in session:
        return redirect('/login-administrador')

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome
        FROM colaboradores
        WHERE status = 'Ativo'
        ORDER BY nome
    """)

    colaboradores = cursor.fetchall()

    conn.close()

    return render_template(
        'administrador/lancar_ponto.html',
        colaboradores=colaboradores
    )

@app.route('/salvar-lancamento-ponto', methods=['POST'])
def salvar_lancamento_ponto():

    if 'administrador_id' not in session:
        return redirect('/login-administrador')

    colaborador_id = request.form['colaborador_id']
    data = request.form['data']
    entrada = request.form['entrada']
    saida_final = request.form['saida_final']
    observacao = request.form['observacao']

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO registros_ponto (
            colaborador_id,
            data,
            entrada,
            saida_final,
            observacao
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        colaborador_id,
        data,
        entrada,
        saida_final,
        observacao
    ))

    conn.commit()
    conn.close()

    return redirect('/lancar-ponto')

@app.route('/enviar-ajuste', methods=['POST'])
def enviar_ajuste():

    if 'colaborador_id' not in session:
        return redirect('/login-colaborador')

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO ajustes_ponto (
            colaborador_id,
            data,
            motivo,
            status
        )
        VALUES (?, ?, ?, ?)
    """, (
        session['colaborador_id'],
        request.form['data'],
        request.form['motivo'],
        'Pendente'
    ))

    conn.commit()
    conn.close()

    return redirect('/meus-ajustes')

@app.route('/primeiro-acesso-gestor')
def primeiro_acesso_gestor():

    if 'gestor_id' not in session:
        return redirect('/login-gestor-nucleo')

    return render_template(
        'gestor_nucleo/primeiro_acesso_gestor.html'
    )

@app.route('/alterar-senha-gestor', methods=['POST'])
def alterar_senha_gestor():

    if 'gestor_id' not in session:
        return redirect('/login-gestor-nucleo')

    senha1 = request.form['senha']
    senha2 = request.form['confirmar_senha']

    if senha1 != senha2:
        return "As senhas não coincidem."

    if senha1 == "Novocolab123":
        return "A senha padrão não pode ser utilizada novamente."

    padrao = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'

    if not re.match(padrao, senha1):

        return """
        A senha deve possuir:

        - mínimo de 8 caracteres;
        - uma letra maiúscula;
        - uma letra minúscula;
        - um número;
        - um caractere especial.
        """

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE gestores
        SET senha = ?
        WHERE id = ?
    """, (
        senha1,
        session['gestor_id']
    ))

    conn.commit()
    conn.close()

    return redirect('/dashboard-gestor-nucleo')

if __name__ == '__main__':
    app.run(debug=True)