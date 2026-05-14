import os
from conexao import get_db_connection
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


# ── Renderização ──────────────────────────────────────────────────────────────

@app.route('/')
def carregar_pagina_inicial():
    return render_template('index.html')


# ── Livros ────────────────────────────────────────────────────────────────────

@app.route('/api/livros', methods=['POST', 'GET'])
def gerenciar_livros():
    if request.method == 'POST':
        dados = request.get_json()
        titulo         = dados.get('titulo')
        autor          = dados.get('autor')
        genero         = dados.get('genero')
        ano_publicacao = dados.get('ano_publicacao')

        if not all([titulo, autor, genero, ano_publicacao]):
            return jsonify({'status': 'error', 'message': 'Todos os campos são obrigatórios'}), 400

        con = get_db_connection()
        con.execute(
            'INSERT INTO livros (titulo, autor, genero, ano_publicacao) VALUES (?, ?, ?, ?)',
            (titulo, autor, genero, ano_publicacao)
        )
        con.commit()
        con.close()
        return jsonify({'status': 'success', 'message': 'Livro cadastrado com sucesso'}), 201

    # GET — suporta combinação de filtros simultaneamente
    busca_livre  = request.args.get('query')
    busca_autor  = request.args.get('autor')
    busca_genero = request.args.get('genero')
    busca_status = request.args.get('status')

    query  = 'SELECT * FROM livros WHERE 1=1'
    params = []

    if busca_status == 'lidos':
        query += ' AND id_livro IN (SELECT id_livro FROM leituras)'
    elif busca_status == 'nao_lidos':
        query += ' AND id_livro NOT IN (SELECT id_livro FROM leituras)'

    if busca_livre:
        query += ' AND (titulo LIKE ? OR autor LIKE ? OR genero LIKE ?)'
        params += [f'%{busca_livre}%', f'%{busca_livre}%', f'%{busca_livre}%']
    elif busca_autor:
        query += ' AND autor LIKE ?'
        params.append(f'%{busca_autor}%')
    elif busca_genero:
        query += ' AND genero LIKE ?'
        params.append(f'%{busca_genero}%')

    con = get_db_connection()
    livros = con.execute(query, params).fetchall()
    con.close()
    return jsonify([dict(l) for l in livros]), 200


@app.route('/api/livros/<int:id_livro>', methods=['GET'])
def gerenciar_livro(id_livro):
    con   = get_db_connection()
    livro = con.execute('SELECT * FROM livros WHERE id_livro = ?', (id_livro,)).fetchone()
    con.close()

    if not livro:
        return jsonify({'status': 'error', 'message': 'Livro não encontrado'}), 404
    return jsonify(dict(livro)), 200


# ── Leituras ──────────────────────────────────────────────────────────────────

@app.route('/api/livros/leituras', methods=['GET'])
def listar_leituras():
    con      = get_db_connection()
    leituras = con.execute('SELECT * FROM leituras').fetchall()
    con.close()
    return jsonify([dict(l) for l in leituras]), 200


@app.route('/api/livros/<int:id_livro>/leituras', methods=['POST', 'PUT'])
def gerenciar_leituras(id_livro):
    con  = get_db_connection()
    dados = request.get_json()

    if request.method == 'POST':
        data_conclusao = dados.get('data_conclusao')
        con.execute(
            'INSERT INTO leituras (id_livro, data_conclusao) VALUES (?, ?)',
            (id_livro, data_conclusao)
        )
        con.commit()
        con.close()
        return jsonify({'status': 'success', 'message': 'Livro marcado como lido!'}), 201

    # PUT — atualiza nota e comentário
    nota       = dados.get('nota')
    comentario = dados.get('comentario', '')

    if nota == None or comentario == None:
        return jsonify({'status': 'error', 'message': 'Todos os campos são obrigatórios!'}), 400
    
    elif 1 >= int(nota) >= 5:
        con.close()
        return jsonify({'status': 'error', 'message': 'Nota deve ser entre 1 e 5'}), 400

    else:
        con.execute(
            'UPDATE leituras SET nota = ?, comentario = ? WHERE id_livro = ?',
            (nota, comentario, id_livro)
        )
    con.commit()
    con.close()
    return jsonify({'status': 'success', 'message': 'Avaliação salva com sucesso!'}), 200


# ── Recomendações ─────────────────────────────────────────────────────────────

@app.route('/api/livros/recomendacoes', methods=['GET'])
def recomendacoes():
    con = get_db_connection()

    # Verifica se há leituras com nota para basear a recomendação
    tem_notas = con.execute(
        'SELECT COUNT(*) FROM leituras WHERE nota IS NOT NULL'
    ).fetchone()[0]

    if not tem_notas:
        con.close()
        return jsonify({
            'livros': [],
            'mensagem': 'Avalie os livros que você leu para receber recomendações personalizadas!'
        }), 200

    # Recomenda livros não lidos do melhor gênero OU dos autores mais bem avaliados
    livros = con.execute('''
        SELECT DISTINCT l.*
        FROM livros l
        WHERE l.id_livro NOT IN (SELECT id_livro FROM leituras)
          AND (
            l.genero = (
                SELECT lv.genero
                FROM livros lv
                JOIN leituras le ON lv.id_livro = le.id_livro
                WHERE le.nota IS NOT NULL
                GROUP BY lv.genero
                ORDER BY AVG(le.nota) DESC
                LIMIT 1
            )
            OR l.autor IN (
                SELECT lv.autor
                FROM livros lv
                JOIN leituras le ON lv.id_livro = le.id_livro
                WHERE le.nota IS NOT NULL
                GROUP BY lv.autor
                ORDER BY AVG(le.nota) DESC
                LIMIT 3
            )
          )
        LIMIT 5
    ''').fetchall()

    con.close()

    if not livros:
        return jsonify({
            'livros': [],
            'mensagem': 'Nenhum livro disponível de acordo com seu histórico. Avalie ou cadastre mais livros!'
        }), 200

    return jsonify({'livros': [dict(l) for l in livros], 'mensagem': ''}), 200


@app.route('/api/livros/recomendacoes/ia', methods=['GET'])
def recomendacoes_ia():
    try:
        from google import genai
    except ImportError:
        return jsonify({'status': 'error', 'message': 'Biblioteca google-genai não instalada.'}), 500

    con = get_db_connection()

    historico = con.execute('''
        SELECT l.titulo, l.autor, l.genero, le.nota, le.comentario
        FROM livros l
        JOIN leituras le ON l.id_livro = le.id_livro
    ''').fetchall()

    nao_lidos = con.execute('''
        SELECT titulo, autor, genero
        FROM livros
        WHERE id_livro NOT IN (SELECT id_livro FROM leituras)
    ''').fetchall()

    con.close()

    if not historico:
        return jsonify({'status': 'error', 'message': 'Nenhum livro lido encontrado.'}), 404

    if not nao_lidos:
        return jsonify({'recomendacao': 'Parabéns! Você já leu todo o acervo. Cadastre novos livros para receber sugestões.'}), 200

    prompt = 'Você é um especialista literário. Aqui está o meu histórico de livros lidos:\n'
    for item in historico:
        linha = f"- Livro: {item['titulo']}, Autor: {item['autor']}, Gênero: {item['genero']}"
        if item['nota']:
            linha += f", Nota: {item['nota']}/5"
        if item['comentario']:
            linha += f", Comentário: '{item['comentario']}'"
        prompt += linha + '\n'

    prompt += '\nLivros disponíveis que ainda não li:\n'
    for livro in nao_lidos:
        prompt += f"- Livro: {livro['titulo']}, Autor: {livro['autor']}, Gênero: {livro['genero']}\n"

    prompt += (
        '\nRegra OBRIGATÓRIA: recomende apenas UM livro, escolhido exclusivamente '
        'da lista acima. Justifique com base nos meus gostos. Máximo de um parágrafo.'
    )

    try:
        api_key = os.environ.get('GEMINI_API_KEY')
        client  = genai.Client(api_key=api_key)
        resposta = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return jsonify({'recomendacao': resposta.text.strip()}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Erro na IA: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)