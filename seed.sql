-- ============================================================
-- Clube do Livro — Seed (dados de exemplo)
-- ============================================================

INSERT INTO livros (titulo, autor, genero, ano_publicacao) VALUES
    ('Dom Quixote',                      'Miguel de Cervantes', 'Aventura',        1605),
    ('Cem Anos de Solidão',              'Gabriel García Márquez', 'Realismo Mágico', 1967),
    ('O Senhor dos Anéis',               'J.R.R. Tolkien',      'Fantasia',        1954),
    ('1984',                             'George Orwell',        'Distopia',        1949),
    ('Orgulho e Preconceito',            'Jane Austen',          'Romance',         1813),
    ('Crime e Castigo',                  'Fiódor Dostoiévski',   'Psicológico',     1866),
    ('O Pequeno Príncipe',               'Antoine de Exupéry',   'Filosofia',       1943),
    ('A Metamorfose',                    'Franz Kafka',          'Realismo Mágico', 1915),
    ('Brave New World',                  'Aldous Huxley',        'Distopia',        1932),
    ('O Nome da Rosa',                   'Umberto Eco',          'Mistério',        1980),
    ('Fahrenheit 451',                   'Ray Bradbury',         'Distopia',        1953),
    ('A Revolução dos Bichos',           'George Orwell',        'Distopia',        1945),
    ('O Processo',                       'Franz Kafka',          'Psicológico',     1925),
    ('Persuasão',                        'Jane Austen',          'Romance',         1817),
    ('A Divina Comédia',                 'Dante Alighieri',      'Poesia Épica',    1320);

-- Leituras com notas (base para as recomendações)
INSERT INTO leituras (id_livro, nota, comentario, data_conclusao) VALUES
    (4, 5, 'Obra-prima. A crítica ao totalitarismo é assustadoramente atual.',   '2025-03-10'),
    (9, 4, 'Belo paralelo com 1984. O condicionamento social é perturbador.',    '2025-04-02'),
    (1, 3, 'Clássico importante, mas achei o ritmo lento em alguns momentos.',   '2025-01-20'),
    (5, 5, 'Austen é brilhante. A ironia e os personagens são perfeitos.',       '2025-02-14'),
    (7, 4, 'Leitura rápida e muito reflexiva. Recomendo para todas as idades.',  '2025-05-01');
