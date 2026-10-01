"""New conservative public-content scan. Report locations/categories, never values."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = {
    'private-key': r'-----BEGIN (?:[A-Z ]+)?PRIVATE KEY-----',
    'github-token': r'\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b',
    'cloud-key': r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
    'api-token': r'\bsk-[A-Za-z0-9_-]{20,}\b',
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
    'machine-user-path': r'/(?:Users|home)/[A-Za-z0-9_.-]+(?:/|\b)',
    'credential-assignment': r'''(?i)\b(?:api[_-]?key|secret|password|passwd|access[_-]?token)\s*[=:]\s*["'][^"']{4,}["']''',
}
FORBIDDEN_SUFFIXES = {'.pdf', '.docx', '.zip', '.npy', '.npz', '.pkl', '.pickle', '.pt', '.pth', '.log'}
IGNORED_PARTS = {'.git', '__pycache__', '.venv', 'new_runs', 'local_data'}


def scan_text(text):
    return [(label, text.count('\n', 0, m.start()) + 1)
            for label, pattern in RULES.items() for m in re.finditer(pattern, text)]


def scan(root):
    findings = []
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root)
        if set(relative.parts) & IGNORED_PARTS:
            continue
        if path.is_symlink():
            findings.append((str(relative), 0, 'symlink'))
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            findings.append((str(relative), 0, 'excluded-file-type'))
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except UnicodeError:
            findings.append((str(relative), 0, 'unexpected-binary'))
            continue
        findings.extend((str(relative), line, label) for label, line in scan_text(text))
    return findings


def main():
    findings = scan(ROOT)
    for path, line, label in findings:
        print(f'RISK {path}:{line} [{label}]')
    if not findings:
        print('PASS: no matched public-content risks in the artifact files. This is a heuristic scan, not a guarantee.')
    return 1 if findings else 0


if __name__ == '__main__':
    raise SystemExit(main())
