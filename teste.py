@app.route('/formulario/<form_id>/Session1', methods=['GET', 'POST']) 
def formulario_SessionOne(form_id):
    global r1,r2,r3,r4,r5
    if request.method == 'POST':
        nome = session.get('nome') ## permanece o nome de usuario da sessao e o telefone
        telefone = session.get('telefone')
        r1 = request.form['S1R1'] ## quando o formulario receber um submit , ele me retorna essas respostas aqui e guarda elas em uma variavel
        r2 = request.form['S1R2']
        r3 = request.form['S1R3']
        r4 = request.form['S1R4']
        r5 = request.form['S1R5']

        with sqlite3.connect('db.sqlite3') as conn:
            c = conn.cursor() 
            # Deleta resposta anterior (se houver)
            c.execute("""
                DELETE FROM respostas
                WHERE formulario_id=? AND nome=? AND telefone=?
            """, (form_id, nome, telefone)) ## se caso tiver uma resposta ele exclui se nao ele deixa quieto0
        print(r1,r2,r3,r5,r4)

    return render_template('sectionOne.html') ## rendeniza o formulario 