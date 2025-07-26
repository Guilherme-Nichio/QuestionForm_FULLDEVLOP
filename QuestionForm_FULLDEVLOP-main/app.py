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
    
            S1Q1 CHAR,
            S1Q2 CHAR,
            S1Q3 CHAR,
            S1Q4 CHAR,
            S1Q5 CHAR,
                  
            S2Q1 CHAR,
            S2Q2 CHAR,
            S2Q3 CHAR,
            S2Q4 CHAR,
                  
            S3Q1 CHAR,
            S3Q2 CHAR,
            S3Q3 CHAR,
            S3Q4 CHAR,
                  
            S4Q1 CHAR,
            S4Q2 CHAR,
            S4Q3 CHAR,
            S4Q4 CHAR,
            S4Q5 CHAR,
            S4Q6 CHAR,
                  
            S5Q1 CHAR,
            S5Q2 CHAR,
            S5Q3 CHAR,
            O_D INTEGER,
            S_R INTEGER,
            P_N INTEGER,
            W_T INTEGER,
            FOREIGN KEY(formulario_id) REFERENCES formularios(id)
        )''')

init_db()

# --- Autenticação ---
## Essa função faz o registro do novo usuario caso o mesmo não exista.
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email'] # ele pede o email e a senha do usuario
        senha = generate_password_hash(request.form['senha']) # aqui pede a senha como dito acima
        try: ## depois ele tenta se conctar como  banco de dados
            with sqlite3.connect('db.sqlite3') as conn: ## caso de certo ele vai pegar o email e a senha do formulario e vai inserir uma nova linha
                conn.execute("INSERT INTO usuarios (email, senha) VALUES (?, ?)", (email, senha))
            return redirect('/login') # como deu certo ele vai pra pagina de login
        except: # se caso der algum erro
            return "Email já cadastrado." # vai me aparecer que o usuario ja esta cadastrado
    return render_template('register.html') # define que essa funcao vai rendenizar o template da pagina de registro ( cadastro de usuario )

## essa funcao abaixo faz o login do usuario
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':  
        email = request.form['email'] # ele pega o email e a senha do usuario que ele colocou nos campos de login
        senha = request.form['senha']
        with sqlite3.connect('db.sqlite3') as conn: # entao o mesmo abre uma conexao com o banco de dados e faz um select
            user = conn.execute("SELECT * FROM usuarios WHERE email=?", (email,)).fetchone() # ele seleciona a todas as coluas onde o email é igual ao email que a pessoa inseriu
            if user and check_password_hash(user[2], senha): ## agora se caso exista um usuario , ou seja nao deu erro ele chega a senha. ele desincripta e ve
                session['user_id'] = user[0] # se caso a senha coincidir ele redireciona para  a pagina principal, no caso o dashboard
                return redirect('/dashboard') # redireciona para a funcao de dashboard
        return "Login inválido." # se nao ele me fala que o login ta invalido 
    return render_template('login.html') # rendeniza a pagina de login

#essa funcao abaixo serve para limpar a conexao do usuario
@app.route('/logout')
def logout():
    session.clear() 
    return redirect('/login') #redireciona para pagina de login

## funcao para trocar a senha ( nao tem muito o que dizer basicamente ele ve se existe um usuario na sessao se caso existir ele )
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
# --- Dashboard ---
## aqui rendeniza a pagina pricipal
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: ## caso a sessao esteja limpa , ou seja nao existir um usuario ele nao vai rendenizar a pagina e vai para a pagina de login
        return redirect('/login')
    with sqlite3.connect('db.sqlite3') as conn: # ele abre uma sessao no banco de dados e seleciona a coluna ID dos formulario , onde o user ID corresponde ao usuario da sessao
        formularios = conn.execute("SELECT id FROM formularios WHERE user_id=?", (session['user_id'],)).fetchall()
   
   #entender melhor o que essa parte faz
        respostas = [] #
        for f in formularios:
            r = conn.execute("SELECT * FROM respostas WHERE formulario_id=?", (f[0],)).fetchall()
            respostas.extend(r)
    return render_template('dashboard.html', respostas=respostas)


# essa parte gera o link dinamico ou seja mostra o link , ( alterar para aparecer em um campo unico )
@app.route('/gerar-link')
def gerar_link():
    if 'user_id' not in session: # mesma coisa se nao tem usuario ele manda pra pagina de login
        return redirect('/login')
    form_id = str(uuid.uuid4()) # gera o id do formulario aleatoriamente com funcao de ID
    with sqlite3.connect('db.sqlite3') as conn: # conecta com o banco de dados 
        conn.execute("INSERT INTO formularios (id, user_id) VALUES (?, ?)", (form_id, session['user_id'])) # cria uma nova linha na tabela de formularios com o id do formulario e o id de quem criou o id do formulario
    link = url_for('formulario_etapa1', form_id=form_id, _external=True) # aqui vai dizer que a pagina que o link vai levar é a etapa 1
    return f"Link do formulário: <a href='{link}'>{link}</a>" # aqui ele retorna o valor do link , em formato de link mesmo  ( alterar para aparecer em um campo no dashboard)
    


# --- Formulário fixo ---
# aqui ele encaminha para o link do formulario 
@app.route('/formulario/<form_id>/etapa1', methods=['GET', 'POST']) ## ele fala que o link vai ser composto por formulario [id ] e a etapa que ele se refere
def formulario_etapa1(form_id):
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']

        # salvar em sessão
        session['form_id'] = form_id
        session['nome'] = nome
        session['telefone'] = telefone # essa etapa salva o id de formulario, o nome e o telefone. no caso para a resposta, nao tem como ir para outra pagina da resposta sem essa primeira etapa ter sido concluida

        with sqlite3.connect('db.sqlite3') as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id FROM respostas
                WHERE formulario_id=? AND nome=? AND telefone=?
            """, (form_id, nome, telefone))
            resposta = cursor.fetchone() ## aqui pegamos o ID das resposta e inserimos o id de formulario , nome e telefone

        if resposta:
            # já existe uma resposta, perguntar se deseja atualizar 
            return redirect(f'/formulario/{form_id}/confirmar-substituicao') ## caso vamos que já existe uma resposta identica ou seja como o mesmo ID de formulario , o mesmo nome e o mesmo telefone ele vai me perguntar se eu desejo substituir a resposta
        else:
            return redirect(f'/formulario/{form_id}/Session1') # caso nao haja resposta ele manda apra uma pagina da etapa 2
    ## SUBSTITUIR POR TEMPLATE DA ETAPA 1
    return '''
        <h2>Identifique-se</h2>
        <form method="post">
            Nome: <input name="nome"><br>
            Telefone: <input name="telefone"><br>
            <button type="submit">Próxima etapa</button>
        </form>
    '''
## aqui é só um retorn para saber se vai desejar substituir mesmo ou se vai continuar com a mesma resposta.
@app.route('/formulario/<form_id>/confirmar-substituicao', methods=['GET', 'POST'])
def confirmar_substituicao(form_id):
    if request.method == 'POST':
        acao = request.form.get('acao')
        if acao == 'sim':
            return redirect(f'/formulario/{form_id}/Session1') # caso a pessoa queira substituir ela vai pra etapa 2
        else:
            session.clear() # caso nao ele limpa a sessao que é as informacoes fornecidas na etapa 1 e fala que anda foi alterado
            return "Resposta não foi alterada."

    return '''
        <h2>Você já respondeu este formulário</h2>
        <p>Deseja responder novamente e substituir a resposta anterior?</p>
        <form method="post">
            <button type="submit" name="acao" value="sim">Sim, quero atualizar</button>
            <button type="submit" name="acao" value="nao">Não</button>
        </form>
    ''' # aqui é só o template de sim ou nao, substiuir por template de confirmação

# esse aqui é um modelo de como vai funcionar as respostas da sessão, sendo elas o seguinte caso vai colocar as respostas de um formulario teste
@app.route('/formulario/<form_id>/etapa2', methods=['GET', 'POST']) # ele continua no mesmo form ID e muda o final do link dizendo que chegou na sessao 2
def formulario_etapa2(form_id):
    if request.method == 'POST':
        nome = session.get('nome') ## permanece o nome de usuario da sessao e o telefone
        telefone = session.get('telefone')
        r1 = request.form['r1'] ## quando o formulario receber um submit , ele me retorna essas respostas aqui e guarda elas em uma variavel
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
            """, (form_id, nome, telefone)) ## se caso tiver uma resposta ele exclui se nao ele deixa quieto

            # Insere nova resposta
            c.execute("""
                INSERT INTO respostas (formulario_id, nome, telefone, r1, r2, r3, r4, r5)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (form_id, nome, telefone, r1, r2, r3, r4, r5))
            conn.commit()

        session.clear()## depoois que ele terminar de inserir ele deixar ele limpa a sessao 
        return "<h3>Resposta atualizada com sucesso!</h3>"

    return render_template('form.html') ## rendeniza o formulario 

## Agora apartir daqui vai o formulario de verdade 
# SESSION 1
@app.route('/formulario/<form_id>/Session1', methods=['GET', 'POST']) 
def formulario_SessionOne(form_id):
    if not session.get('nome'):  # ou session.get('r1') is None
        return redirect(f'/formulario/{form_id}/etapa1')
    if request.method == 'POST':
        session['r1'] = request.form['S1R1']
        session['r2'] = request.form['S1R2']
        session['r3'] = request.form['S1R3']
        session['r4'] = request.form['S1R4']
        session['r5'] = request.form['S1R5']
        return redirect(f'/formulario/{form_id}/Session2')
    return render_template('sectionOne.html')

# SESSION 2
@app.route('/formulario/<form_id>/Session2', methods=['GET', 'POST']) 
def formulario_SessionTwo(form_id):
    if not session.get('nome'):  # ou session.get('r1') is None
        return redirect(f'/formulario/{form_id}/etapa1')    
    if request.method == 'POST':
        session['r6'] = request.form['S2R1']
        session['r7'] = request.form['S2R2']
        session['r8'] = request.form['S2R3']
        session['r9'] = request.form['S2R4']
        return redirect(f'/formulario/{form_id}/Session3')
    return render_template('sectionTwo.html')

# SESSION 3
@app.route('/formulario/<form_id>/Session3', methods=['GET', 'POST']) 
def formulario_SessionThree(form_id):
    if not session.get('nome'):  # ou session.get('r1') is None
        return redirect(f'/formulario/{form_id}/etapa1')
    if request.method == 'POST':
        session['r10'] = request.form['S3R1']
        session['r11'] = request.form['S3R2']
        session['r12'] = request.form['S3R3']
        session['r13'] = request.form['S3R4']
        return redirect(f'/formulario/{form_id}/Session4')
    return render_template('sectionThree.html')

# SESSION 4
@app.route('/formulario/<form_id>/Session4', methods=['GET', 'POST']) 
def formulario_SessionFour(form_id):
    if not session.get('nome'):  # ou session.get('r1') is None
        return redirect(f'/formulario/{form_id}/etapa1')
    if request.method == 'POST':
        session['r14'] = request.form['S4R1']
        session['r15'] = request.form['S4R2']
        session['r16'] = request.form['S4R3']
        session['r17'] = request.form['S4R4']
        session['r18'] = request.form['S4R5']
        session['r19'] = request.form['S4R6']  # Corrigi: estava duplicado 'S4R5'
        return redirect(f'/formulario/{form_id}/Session5')
    return render_template('sectionFour.html')

# SESSION 5 (final)

@app.route('/formulario/<form_id>/Session5', methods=['GET', 'POST']) 
def formulario_SessionFive(form_id):
    if request.method == 'POST':
        session['r20'] = request.form['S5R1']
        session['r21'] = request.form['S5R2']
        session['r22'] = request.form['S5R3']

        respostas = [session.get(f"r{i}") for i in range(1, 23)]
        if None in respostas:
            return redirect(f'/formulario/{form_id}/Session1')

        resultado = calcular_tipo_pele(respostas)

        nome = session.get('nome')
        telefone = session.get('telefone')

        # Conecta ao banco e insere os dados
        conn = sqlite3.connect('db.sqlite3')  # Altere para o nome real
        c = conn.cursor()

        c.execute('''
            INSERT INTO respostas (
                formulario_id, nome, telefone,
                S1Q1, S1Q2, S1Q3, S1Q4, S1Q5,
                S2Q1, S2Q2, S2Q3, S2Q4,
                S3Q1, S3Q2, S3Q3, S3Q4,
                S4Q1, S4Q2, S4Q3, S4Q4, S4Q5, S4Q6,
                S5Q1, S5Q2, S5Q3,
                O_D, S_R, P_N, W_T
            ) VALUES (?, ?, ?,
                      ?, ?, ?, ?, ?,
                      ?, ?, ?, ?,
                      ?, ?, ?, ?,
                      ?, ?, ?, ?, ?, ?,
                      ?, ?, ?,
                      ?, ?, ?, ?)
        ''', (
            form_id, nome, telefone,
            *respostas,  # As 22 respostas (r1 a r22)
            resultado_valor(resultado['O x D']),
            resultado_valor(resultado['S x R']),
            resultado_valor(resultado['P x N']),
            resultado_valor(resultado['W x T'])
        ))

        conn.commit()
        conn.close()

        return render_template('result.html', resultado=resultado)

    return render_template('sectionFive.html')

def resultado_valor(resultado_str):
    """Converte tipo de pele em número para salvar no banco"""
    if "Oleosa" in resultado_str or "O" in resultado_str:
        return 1
    if "Seca" in resultado_str or "D" in resultado_str:
        return 2
    if "Sensível" in resultado_str or "S" in resultado_str:
        return 1
    if "Resistente" in resultado_str or "R" in resultado_str:
        return 2
    if "Pigmentada" in resultado_str or "P" in resultado_str:
        return 1
    if "Não-pigmentada" in resultado_str or "N" in resultado_str:
        return 2
    if "Enrugada" in resultado_str or "W" in resultado_str:
        return 1
    if "Firme" in resultado_str or "T" in resultado_str:
        return 2
    return None



# funcao para calcular o tipo de pele
def calcular_tipo_pele(respostas):
    # Converte letras a/b/c/d em números
    pontuacoes = [ord(r.lower()) - ord('a') + 1 for r in respostas]  # a=1, b=2...

    # Divisões conforme os grupos do gabarito
    O_D = sum(pontuacoes[0:5])     # r1 a r5
    S_R = sum(pontuacoes[5:9])     # r6 a r9
    P_N = sum(pontuacoes[9:13])    # r10 a r13
    W_T = sum(pontuacoes[13:19])   # r14 a r19
    hidratação = pontuacoes[19:22] # r20 a r22 (para contar letras A e B)

    # Resultados dos eixos
    tipo_OD = "Oleosa (O)" if O_D >= 13 else "Seca (D)"
    tipo_SR = "Sensível (S)" if S_R >= 9 else "Resistente (R)"
    tipo_PN = "Pigmentada (P)" if P_N >= 11 else "Não-pigmentada (N)"
    tipo_WT = "Enrugada (W)" if W_T >= 15 else "Firme (T)"
    print(O_D,S_R,P_N,W_T)
    # Hidratação
    qtd_a = hidratação.count(1)
    qtd_b = hidratação.count(2)
    tipo_hidratacao = "Desidratada" if qtd_a > qtd_b else "Equilibrada"

    return {
        'O x D': tipo_OD,
        'S x R': tipo_SR,
        'P x N': tipo_PN,
        'W x T': tipo_WT,
        'Hidratação': tipo_hidratacao
    }

if __name__ == '__main__':
    app.run(debug=True)
