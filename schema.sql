-- ============================================================
-- Clube do Livro — Script de criação das tabelas
-- Execute antes do seed.sql
-- ============================================================

DROP TABLE IF EXISTS leituras;
DROP TABLE IF EXISTS livros;

CREATE TABLE livros (
    id_livro       INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo         TEXT    NOT NULL,
    autor          TEXT    NOT NULL,
    genero         TEXT    NOT NULL,
    ano_publicacao INTEGER NOT NULL
);

CREATE TABLE leituras (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    id_livro       INTEGER NOT NULL UNIQUE,
    nota           INTEGER,
    comentario     TEXT,
    data_conclusao TEXT,
    FOREIGN KEY (id_livro) REFERENCES livros (id_livro)
        ON DELETE CASCADE ON UPDATE CASCADE
);
