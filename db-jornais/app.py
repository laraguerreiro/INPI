import os
import csv
import io
import fitz  # PyMuPDF
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, Response
from database import get_db, init_db, DB_PATH
from pdf_processor import process_pdf, search_terms, extract_pages

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
init_db()

@app.route('/')
def index():
    db = get_db()
    stats = {
        'edicoes': db.execute('SELECT COUNT(*) FROM edicao').fetchone()[0],
        'materias': db.execute('SELECT COUNT(*) FROM materia').fetchone()[0],
        'com_pi': db.execute("SELECT COUNT(*) FROM propriedade_intelectual WHERE menciona_pi='sim'").fetchone()[0],
    }
    recent = db.execute('''
        SELECT m.id, m.titulo, m.autor, m.secao, m.tipo, e.jornal, e.data_edicao
        FROM materia m JOIN edicao e ON m.edicao_id = e.id
        ORDER BY m.criado_em DESC LIMIT 20
    ''').fetchall()
    db.close()
    return render_template('index.html', stats=stats, recent=recent)

@app.route('/importar', methods=['GET', 'POST'])
def importar():
    if request.method == 'POST':
        files = request.files.getlist('pdfs')
        terms_raw = request.form.get('termos', '')
        terms = [t.strip() for t in terms_raw.split(',') if t.strip()]

        results = []
        db = get_db()

        for f in files:
            if not f.filename.endswith('.pdf'):
                continue

            filepath = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)
            f.save(filepath)

            data = process_pdf(filepath, f.filename)
            if not data:
                continue

            # Check if edition already exists
            existing = db.execute('SELECT id FROM edicao WHERE arquivo = ?', (f.filename,)).fetchone()
            if existing:
                edicao_id = existing[0]
            else:
                cur = db.execute(
                    'INSERT INTO edicao (arquivo, jornal, pais, data_edicao, ano) VALUES (?,?,?,?,?)',
                    (data['arquivo'], data['jornal'], data['pais'], data['data_edicao'], data['ano'])
                )
                edicao_id = cur.lastrowid

            # Search terms and create materia entries
            if terms:
                matches = search_terms(data['pages'], terms)
                for match in matches:
                    pages_str = ', '.join(str(p) for p in match.get('page_indices', [match['page_index']]))
                    cur = db.execute(
                        '''INSERT INTO materia (edicao_id, titulo, autor, secao, paginas_pdf, pagina_jornal, texto_completo, tipo)
                           VALUES (?,?,?,?,?,?,?,?)''',
                        (edicao_id, None, match['author'], match['section'],
                         pages_str, match['page_num'], match['text'], None)
                    )
                    materia_id = cur.lastrowid
                    for term in match['matched_terms']:
                        db.execute(
                            'INSERT INTO palavras_chave (materia_id, termo, categoria) VALUES (?,?,?)',
                            (materia_id, term, 'busca')
                        )
                    results.append({
                        'arquivo': f.filename,
                        'pagina': pages_str,
                        'pagina_jornal': match['page_num'],
                        'secao': match['section'],
                        'autor': match['author'],
                        'termos': match['matched_terms'],
                        'multi_page': match.get('multi_page', False),
                        'page_count': match.get('page_count', 1),
                        'trecho': match['text'][:500]
                    })
            else:
                # Import all pages as materias
                for page in data['pages']:
                    from pdf_processor import extract_section, extract_author, extract_page_num
                    db.execute(
                        '''INSERT INTO materia (edicao_id, autor, secao, paginas_pdf, pagina_jornal, texto_completo)
                           VALUES (?,?,?,?,?,?)''',
                        (edicao_id, extract_author(page['text']), extract_section(page['text']),
                         str(page['page_index']), extract_page_num(page['text']), page['text'])
                    )

        db.commit()
        db.close()
        return render_template('resultados.html', results=results, terms=terms)

    return render_template('importar.html')

@app.route('/materias')
def materias():
    db = get_db()
    filtro_jornal = request.args.get('jornal', '')
    filtro_ano = request.args.get('ano', '')
    filtro_termo = request.args.get('termo', '')

    query = '''
        SELECT m.id, m.titulo, m.autor, m.secao, m.tipo, m.pagina_jornal, m.paginas_pdf,
               e.jornal, e.pais, e.data_edicao, e.arquivo
        FROM materia m JOIN edicao e ON m.edicao_id = e.id
        WHERE 1=1
    '''
    params = []
    if filtro_jornal:
        query += ' AND e.jornal = ?'
        params.append(filtro_jornal)
    if filtro_ano:
        query += ' AND e.ano = ?'
        params.append(int(filtro_ano))
    if filtro_termo:
        query += ' AND m.id IN (SELECT materia_id FROM palavras_chave WHERE termo LIKE ?)'
        params.append(f'%{filtro_termo}%')

    query += ' ORDER BY e.data_edicao DESC, m.id'
    materias = db.execute(query, params).fetchall()

    anos = db.execute('SELECT DISTINCT ano FROM edicao WHERE ano IS NOT NULL ORDER BY ano').fetchall()
    db.close()
    return render_template('materias.html', materias=materias, filtro_jornal=filtro_jornal,
                           filtro_ano=filtro_ano, filtro_termo=filtro_termo, anos=anos)

@app.route('/materia/<int:id>')
def materia_detail(id):
    db = get_db()
    materia = db.execute('''
        SELECT m.*, e.jornal, e.pais, e.data_edicao, e.arquivo
        FROM materia m JOIN edicao e ON m.edicao_id = e.id WHERE m.id = ?
    ''', (id,)).fetchone()

    abordagem = db.execute('SELECT * FROM abordagem WHERE materia_id = ?', (id,)).fetchone()
    fontes = db.execute('SELECT * FROM fonte WHERE materia_id = ?', (id,)).fetchall()
    pi = db.execute('SELECT * FROM propriedade_intelectual WHERE materia_id = ?', (id,)).fetchone()
    tecnicas = db.execute('SELECT * FROM tecnica_ia WHERE materia_id = ?', (id,)).fetchall()
    palavras = db.execute('SELECT * FROM palavras_chave WHERE materia_id = ?', (id,)).fetchall()
    db.close()

    return render_template('materia_detail.html', m=materia, abordagem=abordagem,
                           fontes=fontes, pi=pi, tecnicas=tecnicas, palavras=palavras)

@app.route('/materia/<int:id>/editar', methods=['POST'])
def materia_editar(id):
    db = get_db()

    # Update materia basic fields
    db.execute('''UPDATE materia SET titulo=?, autor=?, secao=?, tipo=? WHERE id=?''',
               (request.form.get('titulo'), request.form.get('autor'),
                request.form.get('secao'), request.form.get('tipo'), id))

    # Upsert abordagem
    existing = db.execute('SELECT id FROM abordagem WHERE materia_id=?', (id,)).fetchone()
    if existing:
        db.execute('''UPDATE abordagem SET abordagem=?, gancho=?, sentimento=? WHERE materia_id=?''',
                   (request.form.get('abordagem'), request.form.get('gancho'),
                    request.form.get('sentimento'), id))
    else:
        db.execute('''INSERT INTO abordagem (materia_id, abordagem, gancho, sentimento) VALUES (?,?,?,?)''',
                   (id, request.form.get('abordagem'), request.form.get('gancho'),
                    request.form.get('sentimento')))

    # Upsert propriedade intelectual
    existing = db.execute('SELECT id FROM propriedade_intelectual WHERE materia_id=?', (id,)).fetchone()
    if existing:
        db.execute('''UPDATE propriedade_intelectual SET menciona_pi=?, tipo_pi=?, titular_mencionado=? WHERE materia_id=?''',
                   (request.form.get('menciona_pi'), request.form.get('tipo_pi'),
                    request.form.get('titular_mencionado'), id))
    else:
        db.execute('''INSERT INTO propriedade_intelectual (materia_id, menciona_pi, tipo_pi, titular_mencionado) VALUES (?,?,?,?)''',
                   (id, request.form.get('menciona_pi'), request.form.get('tipo_pi'),
                    request.form.get('titular_mencionado')))

    db.commit()
    db.close()
    return redirect(url_for('materia_detail', id=id))

@app.route('/materia/<int:id>/fonte', methods=['POST'])
def add_fonte(id):
    db = get_db()
    db.execute('''INSERT INTO fonte (materia_id, nome, setor, tipo_fonte, tipo_documento) VALUES (?,?,?,?,?)''',
               (id, request.form.get('nome'), request.form.get('setor'),
                request.form.get('tipo_fonte'), request.form.get('tipo_documento')))
    db.commit()
    db.close()
    return redirect(url_for('materia_detail', id=id))

@app.route('/fonte/<int:id>/excluir', methods=['POST'])
def del_fonte(id):
    db = get_db()
    fonte = db.execute('SELECT materia_id FROM fonte WHERE id=?', (id,)).fetchone()
    materia_id = fonte[0] if fonte else None
    db.execute('DELETE FROM fonte WHERE id=?', (id,))
    db.commit()
    db.close()
    return redirect(url_for('materia_detail', id=materia_id))

@app.route('/materia/<int:id>/tecnica', methods=['POST'])
def add_tecnica(id):
    db = get_db()
    db.execute('INSERT INTO tecnica_ia (materia_id, tecnica) VALUES (?,?)',
               (id, request.form.get('tecnica')))
    db.commit()
    db.close()
    return redirect(url_for('materia_detail', id=id))

@app.route('/materia/<int:id>/excluir', methods=['POST'])
def del_materia(id):
    db = get_db()
    db.execute('DELETE FROM materia WHERE id=?', (id,))
    db.commit()
    db.close()
    return redirect(url_for('materias'))

@app.route('/exportar')
def exportar():
    db = get_db()
    rows = db.execute('''
        SELECT e.arquivo, e.jornal, e.pais, e.data_edicao, e.ano,
               m.id as materia_id, m.titulo, m.autor, m.secao, m.tipo,
               m.pagina_jornal, m.paginas_pdf,
               a.abordagem, a.gancho, a.sentimento,
               pi.menciona_pi, pi.tipo_pi, pi.titular_mencionado
        FROM materia m
        JOIN edicao e ON m.edicao_id = e.id
        LEFT JOIN abordagem a ON a.materia_id = m.id
        LEFT JOIN propriedade_intelectual pi ON pi.materia_id = m.id
        ORDER BY e.data_edicao, m.id
    ''').fetchall()
    db.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['arquivo', 'jornal', 'pais', 'data_edicao', 'ano',
                     'materia_id', 'titulo', 'autor', 'secao', 'tipo',
                     'pagina_jornal', 'paginas_pdf',
                     'abordagem', 'gancho', 'sentimento',
                     'menciona_pi', 'tipo_pi', 'titular_mencionado'])
    for row in rows:
        writer.writerow(list(row))

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='jornais_ia_export.csv'
    )

@app.route('/busca')
def busca():
    return render_template('busca.html')

@app.route('/busca/executar', methods=['POST'])
def busca_executar():
    db = get_db()
    termo = request.form.get('termo', '').strip()
    if not termo:
        return redirect(url_for('busca'))

    materias = db.execute('''
        SELECT m.id, m.titulo, m.autor, m.secao, m.tipo, m.pagina_jornal,
               m.texto_completo, e.jornal, e.data_edicao, e.arquivo
        FROM materia m JOIN edicao e ON m.edicao_id = e.id
        WHERE m.texto_completo LIKE ?
        ORDER BY e.data_edicao DESC
    ''', (f'%{termo}%',)).fetchall()
    db.close()
    return render_template('busca_resultados.html', materias=materias, termo=termo)

@app.route('/pdf-page/<path:filename>/<int:page>')
def pdf_page_image(filename, page):
    """Render a PDF page as PNG image."""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return "PDF não encontrado", 404
    doc = fitz.open(filepath)
    if page < 1 or page > len(doc):
        doc.close()
        return "Página não encontrada", 404
    pg = doc[page - 1]
    # Render at 2x for good quality
    mat = fitz.Matrix(2, 2)
    pix = pg.get_pixmap(matrix=mat)
    img_bytes = pix.tobytes("png")
    doc.close()
    return Response(img_bytes, mimetype='image/png')

if __name__ == '__main__':
    print("Servidor rodando em http://127.0.0.1:5050")
    app.run(debug=False, port=5050)
