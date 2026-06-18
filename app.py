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

@app.route('/login-gestor', methods=['GET', 'POST'])
def login_gestor():

    if request.method == 'POST':

        login = request.form.get('login')
        senha = request.form.get('senha')

        if login == 'gestor1' and senha == 'gestor2026':
            return redirect('/dashboard-gestor')

        return render_template(
            'login_gestor.html',
            erro='Login ou senha inválidos'
        )

    return render_template('login_gestor.html')

@app.route('/login-colaborador', methods=['GET', 'POST'])
def login_colaborador():

    if request.method == 'POST':

        login = request.form.get('login')
        senha = request.form.get('senha')

        from database.conexao import conectar

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM colaboradores
            WHERE login = ?
            AND senha = ?
            AND status = 'Ativo'
        """, (login, senha))

        colaborador = cursor.fetchone()

        conn.close()

        if colaborador:

            session['colaborador_id'] = colaborador[0]
            session['nome'] = colaborador[1]

            # senha padrão = primeiro acesso
            if colaborador[11] == "Novocolab123":
                return redirect('/primeiro-acesso')

            return redirect('/ponto')

        return render_template(
            'login_colaborador.html',
            erro='Login ou senha inválidos'
        )

    return render_template('login_colaborador.html')

@app.route('/cadastro-colaborador')
def cadastro_colaborador():
    return render_template('cadastro_colaborador.html')

@app.route('/dashboard-gestor')
def dashboard_gestor():

    from database.conexao import conectar

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM colaboradores
        WHERE status = 'Ativo'
    """)

    total_colaboradores = cursor.fetchone()[0]

    conn.close()

    return render_template(
        'dashboard_gestor.html',
        total_colaboradores=total_colaboradores
    )

@app.route('/colaboradores')
def colaboradores():

    from database.conexao import conectar

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM colaboradores")

    colaboradores = cursor.fetchall()

    conn.close()

    return render_template(
        'colaboradores.html',
        colaboradores=colaboradores
    )

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

    print("REGISTRO ENCONTRADO:", registro)

    conn.close()

    entrada = "--:--"
    saida_final = "--:--"

    if registro:
        entrada = registro[0] or "--:--"
        saida_final = registro[1] or "--:--"

    return render_template(
        'ponto.html',
        nome=session['nome'],
        entrada=entrada,
        saida_final=saida_final
    )

@app.route('/ajuste-ponto')
def ajuste_ponto():
    return render_template('ajuste_ponto.html')

@app.route('/solicitacoes-ajuste')
def solicitacoes_ajuste():
    return render_template('solicitacoes_ajuste.html')

@app.route('/calendario')
def calendario():
    return render_template('calendario.html')

@app.route('/relatorios')
def relatorios():

    from database.conexao import conectar

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
        'relatorios.html',
        colaboradores=colaboradores,
        registros=None
    )

@app.route('/visualizar-relatorio', methods=['POST'])
def visualizar_relatorio():

    from database.conexao import conectar

    colaborador_id = request.form['colaborador_id']

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome
        FROM colaboradores
        WHERE status = 'Ativo'
        ORDER BY nome
    """)

    colaboradores = cursor.fetchall()

    cursor.execute("""
    SELECT
        data,
        entrada,
        saida_final
    FROM registros_ponto
    WHERE colaborador_id = ?
    ORDER BY id DESC
    """, (colaborador_id,))

    registros = cursor.fetchall()

    print("REGISTROS:", registros)

    cursor.execute("""
    SELECT nome
    FROM colaboradores
    WHERE id = ?
    """, (colaborador_id,))

    nome_colaborador = cursor.fetchone()[0]

    conn.close()

    return render_template(
        'relatorios.html',
        colaboradores=colaboradores,
        registros=registros,
        nome_colaborador=nome_colaborador
    )

@app.route('/salvar-colaborador', methods=['POST'])
def salvar_colaborador():

    from database.conexao import conectar

    conn = conectar()
    cursor = conn.cursor()

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
        request.form['nucleo'],
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

    return redirect('/colaboradores')

@app.route('/cancelar-colaborador/<int:id>')
def cancelar_colaborador(id):

    from database.conexao import conectar

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE colaboradores
        SET status = 'Inativo'
        WHERE id = ?
    """, (id,))

    conn.commit()
    conn.close()

    return redirect('/colaboradores')

@app.route('/editar-colaborador/<int:id>')
def editar_colaborador(id):

    from database.conexao import conectar

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM colaboradores WHERE id = ?",
        (id,)
    )

    colaborador = cursor.fetchone()

    conn.close()

    return render_template(
        'editar_colaborador.html',
        colaborador=colaborador
    )

@app.route('/atualizar-colaborador/<int:id>', methods=['POST'])
def atualizar_colaborador(id):

    from database.conexao import conectar

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

    return redirect('/colaboradores')

from datetime import datetime

@app.route('/registrar-entrada')
def registrar_entrada():

    print("BOTÃO ENTRADA CLICADO")

    if 'colaborador_id' not in session:
        return redirect('/login-colaborador')

    from database.conexao import conectar

    conn = conectar()
    cursor = conn.cursor()

    data_hoje = datetime.now(
    ZoneInfo("America/Sao_Paulo")
).strftime('%d/%m/%Y')
    hora_atual = datetime.now(
    ZoneInfo("America/Sao_Paulo")
).strftime('%H:%M:%S')
    print("HORA SERVIDOR:", datetime.now())

    print("ENTRADA CLICADA")

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

    else:
        print("Registro já existe para hoje")

    conn.close()

    return redirect('/ponto')

@app.route('/registrar-saida-final')
def registrar_saida_final():

    if 'colaborador_id' not in session:
        return redirect('/login-colaborador')

    from database.conexao import conectar
    from datetime import datetime

    conn = conectar()
    cursor = conn.cursor()

    data_hoje = datetime.now(
    ZoneInfo("America/Sao_Paulo")
).strftime('%d/%m/%Y')
    hora_atual = datetime.now(
    ZoneInfo("America/Sao_Paulo")
).strftime('%H:%M:%S')
    print("HORA SERVIDOR:", datetime.now())

    print("SAÍDA CLICADA")

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
        'meu_relatorio.html',
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

    return render_template('primeiro_acesso.html')

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

if __name__ == '__main__':
    app.run(debug=True)