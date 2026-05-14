// ============================================================
// RENDERIZAÇÃO
// ============================================================

let livros_completos = [];
let leituras_completas = [];
let livros_visiveis = 3;
let max_livros_visiveis = Math.min(3, livros_completos.length);

function listar_livros(livros, leituras, mensagemVazia) {
    const container = document.getElementById('container_livros');
    container.innerHTML = '';

    if (livros.length === 0) {
        container.innerHTML = `<p class="vazio">${mensagemVazia}</p>`;
        return;
    }

    const porcao_livros = livros.slice(0, livros_visiveis);

    for (const livro of porcao_livros) {
        const leitura = leituras.find(l => l.id_livro === livro.id_livro);
        const islido  = !!leitura;

        let detalhes_leitura = '';
        let acoes_html       = '';

        if (islido) {
            detalhes_leitura = `<p>Concluído em: ${leitura.data_conclusao}</p>`;
            if (!leitura.nota && !leitura.comentario) {
                acoes_html = `
                    <div class="acoes-livro">
                        <button type="button" class="btn btn-secundario btn-pequeno"
                                onclick="form_avaliacao(${livro.id_livro})">Avaliar Leitura</button>
                    </div>
                    <div id="area_feedback_${livro.id_livro}"></div>
                `;
            } else {
                if (leitura.nota)       detalhes_leitura += `<p>Nota: ${leitura.nota} / 5</p>`;
                if (leitura.comentario) detalhes_leitura += `<p>${leitura.comentario}</p>`;
            }
        } else {
            acoes_html = `
                <div class="acoes-livro">
                    <button type="button" class="btn btn-secundario btn-pequeno"
                            onclick="marcar_lido(${livro.id_livro})">Marcar como Lido</button>
                </div>
                <div id="area_feedback_${livro.id_livro}"></div>
            `;
        }

        const badge = islido
            ? `<span class="badge-status badge-lido">Lido</span>`
            : `<span class="badge-status badge-nao-lido">Não lido</span>`;

        container.innerHTML += `
            <div class="card-livro ${islido ? 'lido' : ''}">
                <h3>${livro.titulo}</h3>
                <p class="meta">${livro.autor} &mdash; ${livro.genero} &mdash; ${livro.ano_publicacao}</p>
                ${badge}
                <div class="detalhes">${detalhes_leitura}</div>
                ${acoes_html}
            </div>
        `;

        }

    if (livros_visiveis < livros.length) {
    container.innerHTML += `<button class = "btn-primario" onclick="mostrar_mais()">
        Mostrar mais (${livros.length - livros_visiveis} restantes)
    </button>`;
    }

    if (livros_visiveis > 3) {
        container.innerHTML += `<button class = "btn-primario" onclick="mostrar_menos()">
            Mostrar menos
        </button>`;
    }
}
        
// ============================================================
// AÇÕES DO USUÁRIO
// ============================================================

async function cadastrar_livro(evento) {
    evento.preventDefault();
    const feedback = document.getElementById('feedback_cadastro');

    const dadosLivro = {
        titulo:         document.getElementById('titulo').value,
        autor:          document.getElementById('autor').value,
        genero:         document.getElementById('genero').value,
        ano_publicacao: parseInt(document.getElementById('ano_publicacao').value)
    };

    try {
        const resposta = await fetch('/api/livros', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(dadosLivro)
        });

        if (resposta.ok) {
            feedback.innerHTML = `<p class="msg msg-sucesso">Livro cadastrado com sucesso!</p>`;
            document.getElementById('form_cadastro_livro').reset();
            buscar_query();
            recomendacoes();
        } else {
            const dados = await resposta.json();
            feedback.innerHTML = `<p class="msg msg-erro">${dados.message}</p>`;
        }
    } catch (erro) {
        console.error('Erro ao cadastrar livro:', erro);
        feedback.innerHTML = `<p class="msg msg-erro">Erro de conexão. Tente novamente.</p>`;
    }
}

async function marcar_lido(id_livro) {
    const data_conclusao = new Date().toISOString().split('T')[0];

    await fetch(`/api/livros/${id_livro}/leituras`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ data_conclusao })
    });

    await buscar_query(false);
}

function form_avaliacao(id_livro) {
    const area = document.getElementById(`area_feedback_${id_livro}`);
    if (!area) return;

    area.innerHTML = `
        <div class="area-avaliacao">
            <p>Como foi a leitura?</p>
            <form onsubmit="enviar_avaliacao(event, ${id_livro})">
                <div class="campo">
                    <label>Nota (1 a 5)</label>
                    <input type="number" name="nota" min="1" max="5" style="width:70px" required>
                </div>
                <div class="campo">
                    <label>Comentário</label>
                    <textarea name="comentario" maxlength="500" required></textarea>
                </div>
                <div class="acoes-livro">
                    <button type="submit" class="btn btn-primario btn-pequeno"
                            style="width:auto">Enviar Avaliação</button>
                </div>
                <div id="feedback_avaliacao_${id_livro}"></div>
            </form>
        </div>
    `;
}

async function enviar_avaliacao(evento, id_livro) {
    evento.preventDefault();
    const form     = evento.target;
    const feedback = document.getElementById(`feedback_avaliacao_${id_livro}`);
    const nota     = form.querySelector('input[name="nota"]').value;
    const comentario = form.querySelector('textarea[name="comentario"]').value;

    const resposta = await fetch(`/api/livros/${id_livro}/leituras`, {
        method:  'PUT',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ nota: nota ? parseInt(nota) : null, comentario })
    });

    if (resposta.ok) {
        await buscar_query(false);
        recomendacoes();
    } else {
        const dados = await resposta.json();
        feedback.innerHTML = `<p class="msg msg-erro">${dados.message}</p>`;
    }
}


// ============================================================
// BUSCA E FILTROS
// ============================================================

async function buscar_query(resetar_funcao = true) {
    const query      = document.getElementById('campo_busca').value;
    const tipo_busca = document.getElementById('filtro').value;
    const radio_lidos     = document.getElementById('radio_lidos').checked;
    const radio_nao_lidos = document.getElementById('radio_nao_lidos').checked;

    let endpoint = '/api/livros';
    const params = new URLSearchParams();

    if (query.trim() !== '') {
        if      (tipo_busca === 'por_autor')  params.set('autor',  query);
        else if (tipo_busca === 'por_genero') params.set('genero', query);
        else                                  params.set('query',  query);
    }

    if      (radio_lidos)     params.set('status', 'lidos');
    else if (radio_nao_lidos) params.set('status', 'nao_lidos');

    if (params.toString()) endpoint += '?' + params.toString();

    try {
        const [resLivros, resLeituras] = await Promise.all([
            fetch(endpoint),
            fetch('/api/livros/leituras')
        ]);

        const livros   = await resLivros.json();
        const leituras = await resLeituras.json();
        livros_completos = livros;
        leituras_completas = leituras;
        if (resetar_funcao) {
            livros_visiveis = 3; // reseta ao buscar
        }
        listar_livros(livros, leituras, 'Nenhum livro encontrado com esses filtros.');
    } catch (erro) {
        console.error('Erro na busca:', erro);
    }
}


// ============================================================
// RECOMENDAÇÕES
// ============================================================

async function recomendacoes() {
    const container = document.getElementById('recomendacoes_de_livros');
    container.innerHTML = '';

    try {
        const resposta = await fetch('/api/livros/recomendacoes');
        const dados    = await resposta.json();

        if (dados.mensagem && dados.livros.length === 0) {
            container.innerHTML = `<p class="msg msg-info">${dados.mensagem}</p>`;
            return;
        }

        dados.livros.forEach(livro => {
            container.innerHTML += `
                <div class="card-recomendacao">
                    <h4>${livro.titulo}</h4>
                    <p class="meta">${livro.autor} &mdash; ${livro.genero} &mdash; ${livro.ano_publicacao}</p>
                </div>
            `;
        });
    } catch (erro) {
        console.error('Erro ao buscar recomendações:', erro);
    }
}

async function chamar_recomendacoes_ia() {
    const container = document.getElementById('recomendacoes_ia');
    container.innerHTML = `<p class="msg msg-info"><em>Consultando o especialista literário...</em></p>`;

    try {
        const resposta = await fetch('/api/livros/recomendacoes/ia');
        const dados    = await resposta.json();

        if (resposta.ok && dados.recomendacao) {
            container.innerHTML = `
                <div class="card-ia">
                    <p>${dados.recomendacao}</p>
                </div>
            `;
        } else {
            container.innerHTML = `<p class="msg msg-info">${dados.message || 'Sem recomendações no momento.'}</p>`;
        }
    } catch (erro) {
        console.error('Erro ao chamar IA:', erro);
        container.innerHTML = `<p class="msg msg-erro">Falha ao conectar com o assistente virtual.</p>`;
    }
}

function mostrar_mais() {
    livros_visiveis += 3;
    listar_livros(livros_completos, leituras_completas, '...');
}

function mostrar_menos() {
    livros_visiveis -= 3;
    if (livros_visiveis <= 3) livros_visiveis = 3;
    listar_livros(livros_completos, leituras_completas, '...');
}