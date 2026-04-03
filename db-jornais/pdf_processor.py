import re
import PyPDF2

def extract_pages(pdf_path):
    """Extract text from each page of a PDF."""
    reader = PyPDF2.PdfReader(pdf_path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ''
        pages.append({
            'page_index': i + 1,
            'text': text
        })
    return pages

def extract_date(text):
    """Extract edition date from page text."""
    months_pt = {
        'janeiro': '01', 'fevereiro': '02', 'março': '03', 'marco': '03',
        'abril': '04', 'maio': '05', 'junho': '06', 'julho': '07',
        'agosto': '08', 'setembro': '09', 'outubro': '10',
        'novembro': '11', 'dezembro': '12',
        'jan': '01', 'fev': '02', 'mar': '03', 'abr': '04',
        'mai': '05', 'jun': '06', 'jul': '07', 'ago': '08',
        'set': '09', 'out': '10', 'nov': '11', 'dez': '12'
    }
    # Long: "2 de Janeiro de 2010"
    m = re.search(r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})', text, re.IGNORECASE)
    if m:
        mon = months_pt.get(m.group(2).lower())
        if mon:
            return f"{m.group(3)}-{mon}-{m.group(1).zfill(2)}"
    # Short: "QUA 24 JUL 2013"
    m = re.search(r'\b(\d{1,2})\s+(jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)\w*\s+(\d{4})', text, re.IGNORECASE)
    if m:
        mon = months_pt.get(m.group(2).lower()[:3])
        if mon:
            return f"{m.group(3)}-{mon}-{m.group(1).zfill(2)}"
    return None

def extract_section(text):
    """Extract section from page header."""
    first200 = text[:200]
    m = re.search(r'\|\s*([A-ZÀ-Ú\s]+?)\s*\|', first200)
    if m:
        return m.group(1).strip()
    m = re.search(r'^(Local\s*\w*)', first200, re.IGNORECASE | re.MULTILINE)
    if m:
        return m.group(1).strip()
    for sec in ['Opinião', 'Desporto', 'Economia', 'Cultura', 'Ciência', 'Sociedade', 'Mundo', 'Portugal']:
        if sec.lower() in first200.lower():
            return sec
    return None

def extract_author(text):
    """Extract author name from text."""
    m = re.search(r'\bPor\s+([A-ZÀ-Ú][a-zà-ú]+(?:\s+[A-ZÀ-Ú][a-zà-ú]+){1,3})', text)
    if m:
        return m.group(1)
    return None

def extract_page_num(text):
    """Extract printed page number."""
    first150 = text[:150]
    m = re.search(r'\b(\d{1,3})\s*\|', first150)
    if m:
        return m.group(1)
    m = re.search(r'\bLocal\w*(\d{1,3})', first150)
    if m:
        return m.group(1)
    return None

def detect_jornal(text, filename):
    """Detect which newspaper this is."""
    text_lower = text.lower()
    if 'público' in text_lower or 'publico' in text_lower:
        return 'Público', 'Portugal'
    if 'folha' in text_lower and ('paulo' in text_lower or 's.paulo' in text_lower):
        return 'Folha de S. Paulo', 'Brasil'
    # Fallback from filename
    fn = filename.lower()
    if 'publico' in fn or fn.startswith('p_'):
        return 'Público', 'Portugal'
    if 'folha' in fn or fn.startswith('f_'):
        return 'Folha de S. Paulo', 'Brasil'
    return None, None

def text_ends_incomplete(text):
    """Check if text ends mid-sentence (article likely continues on next page)."""
    stripped = text.rstrip()
    if not stripped:
        return False
    # Remove common footer patterns (page numbers, ads, etc.)
    lines = stripped.split('\n')
    # Look at last meaningful lines (skip very short lines that might be footers)
    last_meaningful = ''
    for line in reversed(lines):
        line = line.strip()
        if len(line) > 20:
            last_meaningful = line
            break
    if not last_meaningful:
        return False
    # If last meaningful line doesn't end with sentence-ending punctuation, it's incomplete
    return last_meaningful[-1] not in '.!?»"\')'

def next_page_is_continuation(current_text, next_text):
    """Check if next page is a continuation of current page's article."""
    if not next_text or not current_text:
        return False

    # 1. Current page ends mid-sentence
    ends_incomplete = text_ends_incomplete(current_text)

    # 2. Next page starts without a clear new article title
    # New articles usually start with large titles or section headers
    first_200 = next_text[:200].strip()
    has_new_header = bool(re.search(r'\|\s*[A-ZÀ-Ú\s]+?\s*\|', first_200))  # section header like "| CIÊNCIA |"

    # 3. Same section on both pages
    section_current = extract_section(current_text)
    section_next = extract_section(next_text)
    same_section = (section_current and section_next and section_current == section_next)

    # Decision: continuation if text is incomplete AND (same section OR no new header)
    if ends_incomplete and (same_section or not has_new_header):
        return True

    return False

def search_terms(pages, terms):
    """Search for terms in pages, detecting multi-page articles."""
    results = []
    already_included = set()  # track pages already included as continuations

    for i, page in enumerate(pages):
        if page['page_index'] in already_included:
            continue

        text_lower = page['text'].lower()
        matched = [t for t in terms if t.lower() in text_lower]
        if not matched:
            continue

        # Collect all pages of this article
        article_pages = [page['page_index']]
        combined_text = page['text']

        # Check forward: does article continue on next pages?
        j = i
        while j + 1 < len(pages):
            current_text = pages[j]['text']
            next_text = pages[j + 1]['text']
            if next_page_is_continuation(current_text, next_text):
                article_pages.append(pages[j + 1]['page_index'])
                combined_text += '\n\n--- Página ' + str(pages[j + 1]['page_index']) + ' ---\n\n' + next_text
                already_included.add(pages[j + 1]['page_index'])
                # Also check if next page has additional matched terms
                next_lower = next_text.lower()
                for t in terms:
                    if t.lower() in next_lower and t not in matched:
                        matched.append(t)
                j += 1
            else:
                break

        # Check backward: does article start on previous page?
        j = i
        while j - 1 >= 0 and pages[j - 1]['page_index'] not in already_included:
            prev_text = pages[j - 1]['text']
            current_text = pages[j]['text']
            if next_page_is_continuation(prev_text, current_text):
                article_pages.insert(0, pages[j - 1]['page_index'])
                combined_text = pages[j - 1]['text'] + '\n\n--- Página ' + str(pages[j]['page_index']) + ' ---\n\n' + combined_text
                already_included.add(pages[j - 1]['page_index'])
                j -= 1
            else:
                break

        page_nums = ', '.join(str(p) for p in article_pages)
        results.append({
            'page_index': article_pages[0],
            'page_indices': article_pages,
            'text': combined_text,
            'matched_terms': matched,
            'section': extract_section(page['text']),
            'author': extract_author(combined_text),
            'page_num': extract_page_num(page['text']),
            'multi_page': len(article_pages) > 1,
            'page_count': len(article_pages)
        })

    return results

def process_pdf(pdf_path, filename):
    """Full processing of a PDF: extract metadata and pages."""
    pages = extract_pages(pdf_path)
    if not pages:
        return None

    # Get metadata from first page
    first_text = pages[0]['text']
    jornal, pais = detect_jornal(first_text, filename)
    date = None
    for p in pages[:3]:
        date = extract_date(p['text'])
        if date:
            break

    year = int(date[:4]) if date else None

    return {
        'arquivo': filename,
        'jornal': jornal,
        'pais': pais,
        'data_edicao': date,
        'ano': year,
        'pages': pages
    }
