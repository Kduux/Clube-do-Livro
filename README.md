# Clube do Livro

Aplicação web para gerenciamento de leituras pessoais. Permite cadastrar livros, registrar leituras com avaliações e receber recomendações baseadas no seu histórico — com opção de recomendação via inteligência artificial.

---

## Tecnologias

| Camada    | Tecnologia                         |
|-----------|------------------------------------|
| Frontend  | HTML, CSS e JavaScript puro        |
| Backend   | Python 3 + Flask (API REST)        |
| Banco     | SQLite (via módulo `sqlite3`)      |
| IA (bônus)| Google Gemini API (`google-genai`) |

---

## Como rodar localmente

### 1. Pré-requisitos

- Python 3.10 ou superior
- pip

### 2. Clone o repositório

```bash
git clone <url-do-repositorio>
cd trilogo-desafi
```

### 3. Instale as dependências

```bash
pip install flask google-genai
```

### 4. (Opcional) Configure a chave da API do Gemini

A recomendação por IA usa a API do Google Gemini. Se quiser usá-la, exporte sua chave:

```bash
export GEMINI_API_KEY="sua_chave_aqui"
```

Sem isso, a recomendação básica (sem IA) continua funcionando normalmente.

### 5. Crie o banco de dados com os dados de exemplo

```bash
sqlite3 clube_do_livro.db < schema.sql
sqlite3 clube_do_livro.db < seed.sql
```

> **Atenção:** se o arquivo `clube_do_livro.db` já existir de uma versão anterior,
> delete-o antes de executar os comandos acima:
> ```bash
> rm clube_do_livro.db
> ```

### 6. Inicie o servidor

```bash
python app.py
```

Acesse em: [http://localhost:5000](http://localhost:5000)

---

## Endpoints da API

### Livros

| Método | Rota                        | Descrição                          |
|--------|-----------------------------|------------------------------------|
| POST   | `/api/livros`               | Cadastrar um novo livro            |
| GET    | `/api/livros`               | Listar livros (com filtros opcionais) |
| GET    | `/api/livros/<id>`          | Buscar livro por ID                |

**Filtros disponíveis em `GET /api/livros`:**

```
/api/livros                          → todos
/api/livros?status=lidos             → somente lidos
/api/livros?status=nao_lidos         → somente não lidos
/api/livros?autor=Kafka              → por autor
/api/livros?genero=Distopia          → por gênero
/api/livros?query=anel               → busca geral (título, autor ou gênero)
/api/livros?status=lidos&autor=Orwell → filtros combinados
```

### Leituras

| Método | Rota                              | Descrição                         |
|--------|-----------------------------------|-----------------------------------|
| GET    | `/api/livros/leituras`            | Listar todas as leituras          |
| POST   | `/api/livros/<id>/leituras`       | Marcar livro como lido            |
| PUT    | `/api/livros/<id>/leituras`       | Avaliar uma leitura (nota 1–5)    |

### Recomendações

| Método | Rota                              | Descrição                                  |
|--------|-----------------------------------|--------------------------------------------|
| GET    | `/api/livros/recomendacoes`       | Recomendações baseadas no histórico        |
| GET    | `/api/livros/recomendacoes/ia`    | Recomendação gerada por IA com justificativa |

---

## Exemplos de uso (cURL)

```bash
# Cadastrar livro
curl -X POST http://localhost:5000/api/livros \
  -H "Content-Type: application/json" \
  -d '{"titulo":"O Alquimista","autor":"Paulo Coelho","genero":"Filosofia","ano_publicacao":1988}'

# Listar livros não lidos do gênero Distopia
curl "http://localhost:5000/api/livros?status=nao_lidos&genero=Distopia"

# Marcar livro 3 como lido
curl -X POST http://localhost:5000/api/livros/3/leituras \
  -H "Content-Type: application/json" \
  -d '{"data_conclusao":"2026-05-13"}'

# Avaliar o livro 3
curl -X PUT http://localhost:5000/api/livros/3/leituras \
  -H "Content-Type: application/json" \
  -d '{"nota":5,"comentario":"Fantástico, leitura obrigatória."}'

# Buscar recomendações
curl http://localhost:5000/api/livros/recomendacoes

# Recomendação via IA
curl http://localhost:5000/api/livros/recomendacoes/ia
```
