"""New portable runner for recovered legacy code, not final-paper protocols."""
import argparse
import importlib.util
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DEPENDENCIES = {'numpy': 'numpy', 'pandas': 'pandas', 'scipy': 'scipy',
                'scikit-learn': 'sklearn', 'xgboost': 'xgboost',
                'gensim': 'gensim', 'torch': 'torch'}


def missing_dependencies(stage):
    selected = DEPENDENCIES if stage != 'preprocess' else {k: DEPENDENCIES[k] for k in ('numpy', 'pandas')}
    return [name for name, module in selected.items() if importlib.util.find_spec(module) is None]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-root', type=Path)
    parser.add_argument('--work-dir', type=Path)
    parser.add_argument('--stage', choices=['preprocess', 'experiments', 'all'], default='all')
    parser.add_argument('--check-dependencies', action='store_true')
    parser.add_argument('--allow-full-run', action='store_true', help='explicitly allow potentially expensive processing/training')
    args = parser.parse_args()
    missing = missing_dependencies(args.stage)
    if args.check_dependencies:
        print('Missing dependency packages: ' + ', '.join(missing) if missing else 'Dependency names are available; version compatibility and training are not certified.')
        return 2 if missing else 0
    if not args.allow_full_run:
        parser.error('--allow-full-run is required; no dataset processing or training has started')
    if args.work_dir is None or (args.stage != 'experiments' and args.raw_root is None):
        parser.error('--work-dir and, for preprocessing, --raw-root are required')
    if missing:
        print('NOT EXECUTED: missing dependency packages: ' + ', '.join(missing))
        return 2
    work = args.work_dir.resolve()
    if work == ROOT or work.is_relative_to(ROOT / 'legacy_baseline') or work.is_relative_to(ROOT / 'published_tables'):
        parser.error('work directory must not be the artifact root or preserved data/source directories')
    if args.stage in ('preprocess', 'all') and work.exists() and any(work.iterdir()):
        parser.error('preprocessing requires a new or empty work directory')
    if args.stage == 'experiments' and not (work / 'proc').is_dir():
        parser.error('experiments require an existing work-dir/proc from preprocessing')
    if (work / 'out').exists() and any((work / 'out').iterdir()):
        parser.error('refusing to overwrite prior rerun outputs; choose a new work directory')
    if args.stage in ('preprocess', 'all'):
        required = ['HDFS_v1/preprocessed/HDFS.log_templates.csv', 'HDFS_v1/preprocessed/Event_traces.csv', 'BGL/BGL.log']
        if not all((args.raw_root / x).is_file() for x in required):
            parser.error('required dataset files are missing; see data/README.md')
    work.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env.update(LOGAD_PROC_DIR=str(work / 'proc'), LOGAD_OUT_DIR=str(work / 'out'), PYTHONDONTWRITEBYTECODE='1')
    if args.raw_root:
        env['LOGAD_RAW_ROOT'] = str(args.raw_root.resolve())
    scripts = []
    if args.stage in ('preprocess', 'all'):
        scripts += ['build_hdfs.py', 'build_bgl.py']
    if args.stage in ('experiments', 'all'):
        scripts.append('log_experiments.py')
    print('Legacy baseline only. Outputs are new rerun measurements, not final-paper replication.', flush=True)
    for name in scripts:
        print('Running legacy stage: ' + name, flush=True)
        subprocess.run([sys.executable, str(ROOT / 'legacy_baseline/src' / name)], env=env, check=True)
    print('Legacy stages completed; no equality to published final results has been asserted.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
