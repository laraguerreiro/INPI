CREATE TABLE edicao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            arquivo TEXT NOT NULL,
            jornal TEXT,
            pais TEXT,
            data_edicao TEXT,
            ano INTEGER,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE materia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            edicao_id INTEGER NOT NULL,
            titulo TEXT,
            autor TEXT,
            secao TEXT,
            paginas_pdf TEXT,
            pagina_jornal TEXT,
            texto_completo TEXT,
            tipo TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (edicao_id) REFERENCES edicao(id) ON DELETE CASCADE
        );
CREATE TABLE abordagem (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            materia_id INTEGER NOT NULL,
            abordagem TEXT,
            gancho TEXT,
            sentimento TEXT,
            FOREIGN KEY (materia_id) REFERENCES materia(id) ON DELETE CASCADE
        );
CREATE TABLE fonte (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            materia_id INTEGER NOT NULL,
            nome TEXT,
            setor TEXT,
            tipo_fonte TEXT,
            tipo_documento TEXT,
            FOREIGN KEY (materia_id) REFERENCES materia(id) ON DELETE CASCADE
        );
CREATE TABLE propriedade_intelectual (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            materia_id INTEGER NOT NULL,
            menciona_pi TEXT DEFAULT 'nao',
            tipo_pi TEXT,
            titular_mencionado TEXT,
            FOREIGN KEY (materia_id) REFERENCES materia(id) ON DELETE CASCADE
        );
CREATE TABLE tecnica_ia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            materia_id INTEGER NOT NULL,
            tecnica TEXT,
            FOREIGN KEY (materia_id) REFERENCES materia(id) ON DELETE CASCADE
        );
CREATE TABLE palavras_chave (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            materia_id INTEGER NOT NULL,
            termo TEXT,
            categoria TEXT,
            FOREIGN KEY (materia_id) REFERENCES materia(id) ON DELETE CASCADE
        );
