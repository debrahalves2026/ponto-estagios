from flask import Flask, render_template, request, redirect

app = Flask(__name__)

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

@app.route('/login-colaborador')
def login_colaborador():
    return render_template('login_colaborador.html')

@app.route('/cadastro-colaborador')
def cadastro_colaborador():
    return render_template('cadastro_colaborador.html')

@app.route('/dashboard-gestor')
def dashboard_gestor():
    return render_template('dashboard_gestor.html')

@app.route('/colaboradores')
def colaboradores():
    return render_template('colaboradores.html')

@app.route('/ponto')
def ponto():
    return render_template('ponto.html')

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
    return render_template('relatorios.html')

if __name__ == '__main__':
    app.run(debug=True)