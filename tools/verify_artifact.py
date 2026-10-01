"""New standard-library verifier; does not execute experiments."""
import ast
import csv
import hashlib
import json
from pathlib import Path
import sys
from reconstruct_tables import verify
from scan_public import scan

ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    errors = []
    manifest = ROOT / 'SHA256SUMS.txt'
    expected = set()
    for line in manifest.read_text().splitlines():
        wanted, name = line.split('  ', 1)
        path = ROOT / name
        if path.is_absolute() and not path.resolve().is_relative_to(ROOT):
            errors.append('unsafe manifest path')
            continue
        expected.add(name)
        if not path.is_file() or digest(path.read_bytes()) != wanted:
            errors.append('checksum mismatch: ' + name)
    actual = {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()
              and not set(p.relative_to(ROOT).parts) & {'.git', '__pycache__', '.venv', 'new_runs', 'local_data'}
              and p != manifest}
    if actual != expected:
        errors.append('manifest inventory differs')
    provenance = json.loads((ROOT / 'provenance.json').read_text())
    for entry in provenance['archive_entries']:
        content = (ROOT / entry['public_path']).read_text()
        for patch in reversed(entry.get('path_only_patches', [])):
            if content.count(patch['new']) != 1:
                errors.append('portability patch invariant: ' + entry['public_path'])
                break
            content = content.replace(patch['new'], patch['old'], 1)
        if digest(content.encode()) != entry['original_sha256']:
            errors.append('legacy source/result provenance mismatch: ' + entry['public_path'])
    for path in (ROOT / 'legacy_baseline/src').glob('*.py'):
        ast.parse(path.read_text(), filename=path.name)
    with (ROOT / 'legacy_baseline/results/log_results.csv').open() as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 16 or sum(r['setting'] == 'within' for r in rows) != 12:
        errors.append('legacy result dimensions differ')
    for row in rows:
        for metric in ('precision', 'recall', 'f1', 'roc_auc', 'pr_auc', 'tpr_at_1fpr'):
            if not 0 <= float(row[metric]) <= 1:
                errors.append('legacy metric range differs')
    tables = ROOT / 'published_tables'
    result = verify(json.loads((tables / 'tables.json').read_text()), json.loads((tables / 'numeric_ledger.json').read_text()))
    if result != (tables / 'reconstructed_tables.md').read_text():
        errors.append('table presentation differs')
    for path, line, category in scan(ROOT):
        errors.append(f'public-content risk: {path}:{line} [{category}]')
    for error in errors:
        print('FAIL: ' + error)
    if not errors:
        print(f'PASS: {len(expected)} checksummed files; 6 provenance-verified legacy scripts; 16 historical aggregate rows; 8 final aggregate tables; no matched public-content risk.')
        print('Scope: support-artifact integrity and aggregate reconstruction only, not final experiment replication.')
    return bool(errors)


if __name__ == '__main__':
    sys.exit(main())
