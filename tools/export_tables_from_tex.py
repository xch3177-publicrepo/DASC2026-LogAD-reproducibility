"""New export utility, not a generator of experiments or seed-level data.

The input document is not copied to the artifact and its path is not recorded.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
from table_support import command_argument, group, plain, numeric_tokens, token_hash


LABELS = ['datasets', 'access', 'hyper', 'hdfs', 'bgl', 'bglsens', 'cost', 'transfer']


def extract(source):
    blocks = re.findall(r'\\begin\{table\}(?:\[[^]]*\])?.*?\\end\{table\}', source, re.S)
    if len(blocks) != 8:
        raise ValueError('expected exactly eight table environments')
    tables, ledger, source_ledger, layout_tokens, layout_positions, pairs = [], [], [], [], [], []
    for number, block in enumerate(blocks, 1):
        label = command_argument(block, r'\label')
        if label != 'tab:' + LABELS[number - 1]:
            raise ValueError('unexpected table order')
        tabular = re.search(r'\\begin\{tabular\}(.*?)\\end\{tabular\}', block, re.S).group(1)
        _, end = group(tabular, tabular.index('{'))
        tabular = tabular[end:]
        tabular = re.sub(r'\\cmidrule(?:\([lr]+\))?\{[\d-]+\}', '', tabular)
        # Independent numeric ledger uses the original tabular text, with
        # layout-only metadata removed exactly as the manuscript gate does.
        audited = re.sub(r'\\multicolumn\{\d+\}', r'\\multicolumn', tabular)
        numeric_matches = list(re.finditer(r'\d[\d,]*(?:\.\d+)?|\.\d+', audited))
        for spacing in re.finditer(r'\\hspace\{([^}]*)\}', audited):
            for index, match in enumerate(numeric_matches):
                if spacing.start() <= match.start() < spacing.end():
                    layout_positions.append(len(source_ledger) + index)
                    layout_tokens.append(match.group())
        source_ledger.extend(numeric_tokens(audited))
        audited = re.sub(r'\\hspace\{[^}]*\}', '', audited)
        ledger.extend(numeric_tokens(audited))
        pairs.extend([list(p) for p in re.findall(
            r'(-?[\d.,]*\d)\s*\$\\pm\$\s*(-?[\d.,]*\d)', audited)])
        tabular = re.sub(r'\\(?:toprule|midrule|bottomrule|rowhead|rowalt|rowpanelA|rowpanelB)\b', '', tabular)
        rows = []
        for row in re.split(r'\\\\', tabular):
            if not row.strip():
                continue
            cells = []
            for cell in row.split('&'):
                cell = cell.strip()
                span = 1
                if cell.startswith(r'\multicolumn'):
                    pos = len(r'\multicolumn')
                    count, pos = group(cell, pos)
                    _, pos = group(cell, pos)
                    body, pos = group(cell, pos)
                    span = int(count)
                    cell = body + cell[pos:]
                cells.append({'text': plain(cell), 'span': span})
            rows.append({'cells': cells})
        table = {'number': number, 'label': label, 'caption': plain(command_argument(block, r'\caption')),
                 'rows': rows, 'source_table_sha256': hashlib.sha256(block.encode()).hexdigest()}
        if number == 2:
            table['notes'] = ['* Scored labels are hidden; transductive access uses unlabeled scored-data artifacts (Section IV).']
        tables.append(table)
    if len(ledger) != 344 or len(source_ledger) != 348 or layout_tokens != ['0.6'] * 4 or len(pairs) != 134:
        raise ValueError(f'ledger mismatch: {len(ledger)} numeric tokens / {len(pairs)} mean-SD pairs')
    return ({'schema': 1, 'scope': 'published aggregate reconstruction, not experiment replay', 'tables': tables},
            {'schema': 1, 'numeric_tokens': ledger, 'mean_sd_pairs': pairs,
             'numeric_tokens_sha256': token_hash(ledger), 'mean_sd_pairs_sha256': token_hash(pairs),
             'legacy_source_numeric_tokens': source_ledger,
             'legacy_source_numeric_tokens_sha256': token_hash(source_ledger),
             'excluded_layout_tokens': layout_tokens,
             'excluded_layout_positions': layout_positions,
             'note': '348 legacy source-audit numeric tokens include four 0.6em spacing parameters; 344 numeric tokens occur in visible table cells.'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parents[1] / 'published_tables')
    args = parser.parse_args()
    document, ledger = extract(args.source.read_text(encoding='utf-8'))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, data in [('tables.json', document), ('numeric_ledger.json', ledger)]:
        (args.output_dir / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Exported 8 aggregate tables; 344 visible numeric tokens / 134 mean-SD pairs; 348 legacy source tokens include four spacing parameters. No experiment executed.')


if __name__ == '__main__':
    main()
