from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import date
import math
import re


app = Flask(__name__)
app.secret_key = 'chavesecretaproladraonaomeroubar'

# Dados em memória
usuarios = []
receitas = []
despesas = []

# ----------------- HOME -----------------
@app.route('/')
def home():
    if 'usuario' in session:
        return redirect(url_for('home_usuario'))
    return render_template('home.html')

@app.route('/home_usuario')
def home_usuario():
    if 'usuario' not in session:
        return redirect(url_for('entrar'))
    return render_template('home_usuario.html')

# ----------------- AUTENTICAÇÃO -----------------
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome'].strip()
        email = request.form['email'].strip()
        cpf = request.form['cpf'].strip()
        telefone = request.form['telefone'].strip()
        senha = request.form['senha']
        confirmar = request.form['confirmar_senha']

        if not all([nome, email, cpf, telefone, senha, confirmar]):
            flash('Preencha todos os campos.', 'erro')
            return redirect(url_for('cadastro'))

        if not cpf.isdigit():
            flash('O campo CPF deve conter apenas números.', 'erro')
            return redirect(url_for('cadastro'))

        if len(senha) < 8 or not re.search(r'[A-Z]', senha) or not re.search(r'[a-z]', senha) \
           or not re.search(r'\d', senha) or not re.search(r'\W', senha):
            flash('A senha precisa conter letras maiúsculas, minúsculas, número e símbolo.', 'erro')
            return redirect(url_for('cadastro'))

        if senha != confirmar:
            flash('As senhas não coincidem.', 'erro')
            return redirect(url_for('cadastro'))

        for u in usuarios:
            if u['email'] == email:
                flash('Email já cadastrado.', 'erro')
                return redirect(url_for('cadastro'))

        usuarios.append({'nome': nome, 'email': email, 'cpf': cpf, 'telefone': telefone, 'senha': senha})
        session['usuario'] = email
        return redirect(url_for('home_usuario'))

    return render_template('cadastro.html')

@app.route('/entrar', methods=['GET', 'POST'])
def entrar():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        for u in usuarios:
            if u['email'] == email and u['senha'] == senha:
                session['usuario'] = email
                return redirect(url_for('home_usuario'))

        flash('Email ou senha incorretos.', 'erro')
    return render_template('login.html')

@app.route('/sair')
def sair():
    session.pop('usuario', None)
    return redirect(url_for('home'))

# ----------------- PERFIL -----------------
@app.route('/perfil')
def perfil():
    if 'usuario' not in session:
        return redirect(url_for('entrar'))

    usuario = next((u for u in usuarios if u['email'] == session['usuario']), None)
    if not usuario:
        flash('Usuário não encontrado.', 'erro')
        return redirect(url_for('sair'))

    return render_template('perfil.html', usuario=usuario)


@app.route('/editar_perfil', methods=['GET', 'POST'])
def editar_perfil():
    if 'usuario' not in session:
        return redirect(url_for('entrar'))

    usuario = next(u for u in usuarios if u['email'] == session['usuario'])

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        cpf = request.form['cpf']
        telefone = request.form['telefone']
        senha = request.form['senha']

        if not cpf.isdigit():
            flash('CPF deve conter apenas números.', 'erro')
            return redirect(url_for('editar_perfil'))

        usuario['nome'] = nome
        usuario['email'] = email
        usuario['cpf'] = cpf
        usuario['telefone'] = telefone
        usuario['senha'] = senha

        session['usuario'] = email
        flash('Perfil atualizado!', 'sucesso')
        return redirect(url_for('perfil'))

    return render_template('editar_perfil.html', usuario=usuario)

# ----------------- RECEITAS -----------------
@app.route('/receitas')
def listar_receitas():
    if 'usuario' not in session:
        return redirect(url_for('entrar'))
    lista = [r for r in receitas if r['usuario'] == session['usuario']]
    return render_template('receitas.html', receitas=lista)

@app.route('/adicionar_receita', methods=['GET', 'POST'])
def adicionar_receita():
    if request.method == 'POST':
        descricao = request.form['descricao']
        valor = request.form['valor']
        data = request.form['data']

        try:
            valor = float(valor)
            if valor < 0:
                raise ValueError
        except ValueError:
            flash('Informe um valor válido e positivo.', 'erro')
            return redirect(url_for('adicionar_receita'))

        receitas.append({
            'id': len(receitas)+1,
            'descricao': descricao,
            'valor': valor,
            'data': data,
            'usuario': session['usuario']
        })
        return redirect(url_for('listar_receitas'))

    return render_template('adicionar_receita.html')

@app.route('/editar_receita/<int:id>', methods=['GET', 'POST'])
def editar_receita(id):
    receita = next(r for r in receitas if r['id'] == id)

    if request.method == 'POST':
        receita['descricao'] = request.form['descricao']
        receita['valor'] = float(request.form['valor'])
        receita['data'] = request.form['data']
        return redirect(url_for('listar_receitas'))

    return render_template('editar_receita.html', receita=receita)

@app.route('/excluir_receita/<int:id>')
def excluir_receita(id):
    global receitas
    receitas = [r for r in receitas if r['id'] != id]
    return redirect(url_for('listar_receitas'))

# ----------------- DESPESAS -----------------
@app.route('/despesas')
def listar_despesas():
    if 'usuario' not in session:
        return redirect(url_for('entrar'))
    lista = [d for d in despesas if d['usuario'] == session['usuario']]
    return render_template('despesas.html', despesas=lista)

@app.route('/adicionar_despesa', methods=['GET', 'POST'])
def adicionar_despesa():
    if request.method == 'POST':
        descricao = request.form['descricao']
        valor = request.form['valor']
        data = request.form['data'] or str(date.today())

        try:
            valor = float(valor)
            if valor < 0:
                raise ValueError
        except ValueError:
            flash('Informe um valor válido e positivo.', 'erro')
            return redirect(url_for('adicionar_despesa'))

        despesas.append({
            'id': len(despesas)+1,
            'descricao': descricao,
            'valor': valor,
            'data': data,
            'usuario': session['usuario']
        })
        return redirect(url_for('listar_despesas'))

    return render_template('adicionar_despesa.html')

@app.route('/editar_despesa/<int:id>', methods=['GET', 'POST'])
def editar_despesa(id):
    despesa = next(d for d in despesas if d['id'] == id)

    if request.method == 'POST':
        despesa['descricao'] = request.form['descricao']
        despesa['valor'] = float(request.form['valor'])
        despesa['data'] = request.form['data']
        return redirect(url_for('listar_despesas'))

    return render_template('editar_despesa.html', despesa=despesa)

@app.route('/excluir_despesa/<int:id>')
def excluir_despesa(id):
    global despesas
    despesas = [d for d in despesas if d['id'] != id]
    return redirect(url_for('listar_despesas'))


@app.route('/calculadora', methods=['GET', 'POST'])
def calculadora():
    if 'usuario' not in session:
        return redirect(url_for('entrar'))

    resultado = None

    if request.method == 'POST':
        try:
            # Obter dados do formulário
            gastos = float(request.form['gastos'])
            reserva_atual = float(request.form['atual'])
            renda = float(request.form['renda'])
            meses_cobertura = int(request.form['meses'])

            # Cálculos
            reserva_necessaria = gastos * meses_cobertura
            valor_a_poupar = max(0, reserva_necessaria - reserva_atual)

            # Calcular tempo e valor mensal (considerando 20% da renda como poupança máxima)
            poupanca_maxima = renda * 0.2
            if poupanca_maxima > 0:
                tempo_estimado = math.ceil(valor_a_poupar / poupanca_maxima)
                valor_mensal = min(poupanca_maxima, valor_a_poupar)
            else:
                tempo_estimado = 0
                valor_mensal = 0

            # Preparar resultado
            resultado = {
                'necessaria': reserva_necessaria,
                'a_poupar': valor_a_poupar,
                'tempo': tempo_estimado,
                'mensal': valor_mensal
            }

        except ValueError:
            flash('Por favor, insira valores válidos em todos os campos', 'erro')

    return render_template('calculadora.html', resultado=resultado)

# ----------------- CARTEIRA -----------------
@app.route('/carteira')
def carteira():
    if 'usuario' not in session:
        return redirect(url_for('entrar'))

    usuario = session['usuario']
    total_receitas = sum(r['valor'] for r in receitas if r['usuario'] == usuario)
    total_despesas = sum(d['valor'] for d in despesas if d['usuario'] == usuario)
    saldo = total_receitas - total_despesas

    return render_template('carteira.html', saldo=saldo, receitas=total_receitas, despesas=total_despesas)

if __name__ == '__main__':
    app.run(debug=True)
