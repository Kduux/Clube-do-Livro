import sqlite3 as sql


def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados."""
    con = sql.connect('clube_do_livro.db')
    con.row_factory = sql.Row
    return con


def init_db():
    """Inicializa as tabelas do banco de dados, se não existirem."""
    con = get_db_connection()

    con.execute('''
        CREATE TABLE IF NOT EXISTS livros (
            id_livro       INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo         TEXT    NOT NULL,
            autor          TEXT    NOT NULL,
            genero         TEXT    NOT NULL,
            ano_publicacao INTEGER NOT NULL
        )
    ''')

    con.execute('''
        CREATE TABLE IF NOT EXISTS leituras (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            id_livro       INTEGER NOT NULL UNIQUE,
            nota           INTEGER,
            comentario     TEXT,
            data_conclusao TEXT,
            FOREIGN KEY (id_livro) REFERENCES livros (id_livro)
                ON DELETE CASCADE ON UPDATE CASCADE
        )
    ''')

    con.commit()
    con.close()



init_db()