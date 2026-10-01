"""New deterministic presentation of exported aggregates; not experiment replay."""
import argparse
import json
from pathlib import Path
from table_support import canonical_cells, markdown, mean_sd, numeric_tokens, token_hash

ROOT = Path(__file__).resolve().parents[1]


def verify(document, ledger):
    tables = document['tables']
    if len(tables) != 8 or [t['number'] for t in tables] != list(range(1, 9)):
        raise ValueError('table count or ordering differs')
    cells = canonical_cells(tables)
    tokens = numeric_tokens(' '.join(cells))
    pairs = mean_sd(cells)
    if tokens != ledger['numeric_tokens'] or len(tokens) != 344:
        raise ValueError('ordered numeric ledger differs')
    if pairs != ledger['mean_sd_pairs'] or len(pairs) != 134:
        raise ValueError('ordered mean-SD ledger differs')
    if token_hash(tokens) != ledger['numeric_tokens_sha256']:
        raise ValueError('numeric ledger checksum differs')
    if token_hash(pairs) != ledger['mean_sd_pairs_sha256']:
        raise ValueError('mean-SD ledger checksum differs')
    source_tokens = ledger['legacy_source_numeric_tokens']
    if len(source_tokens) != 348 or token_hash(source_tokens) != ledger['legacy_source_numeric_tokens_sha256']:
        raise ValueError('legacy source ledger differs')
    if ledger['excluded_layout_tokens'] != ['0.6'] * 4:
        raise ValueError('layout-token accounting differs')
    positions = ledger['excluded_layout_positions']
    if len(set(positions)) != 4 or [source_tokens[i] for i in positions] != ['0.6'] * 4:
        raise ValueError('layout-token positions differ')
    if [token for i, token in enumerate(source_tokens) if i not in positions] != tokens:
        raise ValueError('source/display ledgers do not reconcile')
    return markdown(document)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='compare without writing')
    args = parser.parse_args()
    data = ROOT / 'published_tables'
    result = verify(json.loads((data / 'tables.json').read_text()), json.loads((data / 'numeric_ledger.json').read_text()))
    output = data / 'reconstructed_tables.md'
    if args.check:
        if not output.is_file() or output.read_text() != result:
            raise SystemExit('FAIL: reconstructed Markdown is missing or differs')
    else:
        output.write_text(result, encoding='utf-8')
    print('PASS: 8 aggregate tables, 344 visible numeric tokens, 134 mean-SD pairs; 348 legacy source tokens include four spacing parameters; Markdown matches.')


if __name__ == '__main__':
    main()
