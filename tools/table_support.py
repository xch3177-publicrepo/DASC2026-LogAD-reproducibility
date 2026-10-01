"""New 2026-10-01 aggregate-export helpers; not experiment code."""
import hashlib
import json
import re


def group(text, start):
    if text[start] != '{':
        raise ValueError('expected opening brace')
    depth = 1
    i = start + 1
    while i < len(text):
        if text[i] == '\\':
            i += 2
            continue
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return text[start + 1:i], i + 1
        i += 1
    raise ValueError('unclosed brace group')


def command_argument(text, command):
    m = re.search(re.escape(command) + r'\s*\{', text)
    if not m:
        raise ValueError('missing command: ' + command)
    return group(text, m.end() - 1)[0]


def numeric_tokens(text):
    return re.findall(r'\d[\d,]*(?:\.\d+)?|\.\d+', text)


def token_hash(tokens):
    return hashlib.sha256(json.dumps(tokens, separators=(',', ':')).encode()).hexdigest()


def plain(text):
    text = re.sub(r'\\hspace\{[^}]*\}', '', text)
    text = text.replace(r'\%', '%').replace(r'\pm', '±')
    text = text.replace(r'\rightarrow', '→').replace(r'\,', ' ')
    text = text.replace(r'\times', '×').replace('~', ' ')
    for command in ('mbox', 'textsuperscript', 'textit', 'textbf'):
        while re.search(r'\\' + command + r'\{', text):
            m = re.search(r'\\' + command + r'\{', text)
            body, end = group(text, m.end() - 1)
            text = text[:m.start()] + body + text[end:]
    text = text.replace('$', '').replace('{', '').replace('}', '')
    if '\\' in text:
        raise ValueError('unhandled markup in exported cell/caption')
    return ' '.join(text.split())


def canonical_cells(tables):
    return [cell['text'] for table in tables for row in table['rows']
            for cell in row['cells']]


def mean_sd(cells):
    return [list(p) for text in cells
            for p in re.findall(r'(-?[\d.,]*\d)\s*±\s*(-?[\d.,]*\d)', text)]


def markdown(document):
    lines = ['# Published aggregate tables', '',
             'Reconstructed from exported final-paper aggregates. This is not an experiment rerun.', '']
    for table in document['tables']:
        lines += [f"## Table {table['number']}: {table['caption']}", '']
        width = max(sum(cell['span'] for cell in row['cells']) for row in table['rows'])
        lines.append('| ' + ' | '.join(f'Column {i + 1}' for i in range(width)) + ' |')
        lines.append('| ' + ' | '.join('---' for _ in range(width)) + ' |')
        for row in table['rows']:
            values = []
            for cell in row['cells']:
                values.append(cell['text'].replace('|', r'\|'))
                values.extend([''] * (cell['span'] - 1))
            values.extend([''] * (width - len(values)))
            lines.append('| ' + ' | '.join(values) + ' |')
        lines.append('')
        for note in table.get('notes', []):
            lines += [note, '']
    return '\n'.join(lines).rstrip() + '\n'
