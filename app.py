from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, uuid

app = Flask(__name__)
app.secret_key = 'segredo-supersecreto'

def init_db():
    with sqlite3.connect('db.sqlite3') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT UNIQUE NOT NULL,
                        senha TEXT NOT NULL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS formularios (
                        id TEXT PRIMARY KEY,
                        user_id INTEGER,
                        FOREIGN KEY(user_id) REFERENCES usuarios(id))''')
        c.execute('''CREATE TABLE IF NOT EXISTS respostas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            formulario_id TEXT,
            nome TEXT,
            telefone TEXT,
            r1 TEXT, r2 TEXT, r3 TEXT, r4 TEXT, r5 TEXT,
            FOREIGN KEY(formulario_id) REFERENCES formularios(id)
        )''')

init_db()

# --- Autenticação ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        senha = generate_password_hash(request.form['senha'])
        try:
            with sqlite3.connect('db.sqlite3') as conn:
                conn.execute("INSERT INTO usuarios (email, senha) VALUES (?, ?)", (email, senha))
            return redirect('/login')
        except:
            return "Email já cadastrado."
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        with sqlite3.connect('db.sqlite3') as conn:
            user = conn.execute("SELECT * FROM usuarios WHERE email=?", (email,)).fetchone()
            if user and check_password_hash(user[2], senha):
                session['user_id'] = user[0]
                return redirect('/dashboard')
        return "Login inválido."
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# --- Dashboard ---
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    with sqlite3.connect('db.sqlite3') as conn:
        formularios = conn.execute("SELECT id FROM formularios WHERE user_id=?", (session['user_id'],)).fetchall()
        respostas = []
        for f in formularios:
            r = conn.execute("SELECT * FROM respostas WHERE formulario_id=?", (f[0],)).fetchall()
            respostas.extend(r)
    return render_template('dashboard.html', respostas=respostas)

@app.route('/gerar-link')
def gerar_link():
    if 'user_id' not in session:
        return redirect('/login')
    form_id = str(uuid.uuid4())
    with sqlite3.connect('db.sqlite3') as conn:
        conn.execute("INSERT INTO formularios (id, user_id) VALUES (?, ?)", (form_id, session['user_id']))
    link = url_for('formulario_etapa1', form_id=form_id, _external=True)
    return f"Link do formulário: <a href='{link}'>{link}</a>"
    
@app.route('/trocar-senha', methods=['GET', 'POST'])
def trocar_senha():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        senha_atual = request.form['senha_atual']
        nova_senha = request.form['nova_senha']

        with sqlite3.connect('db.sqlite3') as conn:
            user = conn.execute("SELECT senha FROM usuarios WHERE id=?", (session['user_id'],)).fetchone()
            if not user or not check_password_hash(user[0], senha_atual):
                return "Senha atual incorreta!"

            nova_hash = generate_password_hash(nova_senha)
            conn.execute("UPDATE usuarios SET senha=? WHERE id=?", (nova_hash, session['user_id']))
            conn.commit()

        return "Senha atualizada com sucesso!"

    return '''
    <h2>Trocar senha</h2>
    <form method="post">
        Senha atual: <input type="password" name="senha_atual"><br>
        Nova senha: <input type="password" name="nova_senha"><br><br>
        <button type="submit">Atualizar senha</button>
    </form>
    '''

# --- Formulário fixo ---
@app.route('/formulario/<form_id>/etapa1', methods=['GET', 'POST'])
def formulario_etapa1(form_id):
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']

        # salvar em sessão
        session['form_id'] = form_id
        session['nome'] = nome
        session['telefone'] = telefone

        with sqlite3.connect('db.sqlite3') as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id FROM respostas
                WHERE formulario_id=? AND nome=? AND telefone=?
            """, (form_id, nome, telefone))
            resposta = cursor.fetchone()

        if resposta:
            # já existe uma resposta, perguntar se deseja atualizar
            return redirect(f'/formulario/{form_id}/confirmar-substituicao')
        else:
            return redirect(f'/formulario/{form_id}/etapa2')

    return '''
        <h2>Identifique-se</h2>
        <form method="post">
            Nome: <input name="nome"><br>
            Telefone: <input name="telefone"><br>
            <button type="submit">Próxima etapa</button>
        </form>
    '''

@app.route('/formulario/<form_id>/confirmar-substituicao', methods=['GET', 'POST'])
def confirmar_substituicao(form_id):
    if request.method == 'POST':
        acao = request.form.get('acao')
        if acao == 'sim':
            return redirect(f'/formulario/{form_id}/etapa2')
        else:
            session.clear()
            return "Resposta não foi alterada."

    return '''
        <h2>Você já respondeu este formulário</h2>
        <p>Deseja responder novamente e substituir a resposta anterior?</p>
        <form method="post">
            <button type="submit" name="acao" value="sim">Sim, quero atualizar</button>
            <button type="submit" name="acao" value="nao">Não</button>
        </form>
    '''
@app.route('/formulario/<form_id>/etapa2', methods=['GET', 'POST'])
def formulario_etapa2(form_id):
    if request.method == 'POST':
        nome = session.get('nome')
        telefone = session.get('telefone')
        r1 = request.form['r1']
        r2 = request.form['r2']
        r3 = request.form['r3']
        r4 = request.form['r4']
        r5 = request.form['r5']

        with sqlite3.connect('db.sqlite3') as conn:
            c = conn.cursor()
            # Deleta resposta anterior (se houver)
            c.execute("""
                DELETE FROM respostas
                WHERE formulario_id=? AND nome=? AND telefone=?
            """, (form_id, nome, telefone))

            # Insere nova resposta
            c.execute("""
                INSERT INTO respostas (formulario_id, nome, telefone, r1, r2, r3, r4, r5)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (form_id, nome, telefone, r1, r2, r3, r4, r5))
            conn.commit()

        session.clear()
        return "<h3>Resposta atualizada com sucesso!</h3>"

    return render_template('form.html')

if __name__ == '__main__':
    app.run(debug=True)