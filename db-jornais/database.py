import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'jornais_ia.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS edicao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            arquivo TEXT NOT NULL,
            jornal TEXT,
            pais TEXT,
            data_edicao TEXT,
            ano INTEGER,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS materia (
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

        CREATE TABLE IF NOT EXISTS abordagem (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            materia_id INTEGER NOT NULL,
            abordagem TEXT,
            gancho TEXT,
            sentimento TEXT,
            FOREIGN KEY (materia_id) REFERENCES materia(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS fonte (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            materia_id INTEGER NOT NULL,
            nome TEXT,
            setor TEXT,
            tipo_fonte TEXT,
            tipo_documento TEXT,
            FOREIGN KEY (materia_id) REFERENCES materia(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS propriedade_intelectual (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            materia_id INTEGER NOT NULL,
            menciona_pi TEXT DEFAULT 'nao',
            tipo_pi TEXT,
            titular_mencionado TEXT,
            FOREIGN KEY (materia_id) REFERENCES materia(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS tecnica_ia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            materia_id INTEGER NOT NULL,
            tecnica TEXT,
            FOREIGN KEY (materia_id) REFERENCES materia(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS palavras_chave (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            materia_id INTEGER NOT NULL,
            termo TEXT,
            categoria TEXT,
            FOREIGN KEY (materia_id) REFERENCES materia(id) ON DELETE CASCADE
        );
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Banco de dados criado com sucesso!")
