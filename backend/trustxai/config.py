from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / 'research/step-04/clinical-cdss'
RUNTIME = Path(os.environ.get('TRUSTXAI_RUNTIME', str(ROOT / '.trustxai-runtime'))).expanduser()
APP_DATA = Path(os.environ.get('TRUSTXAI_APP_DATA', str(RUNTIME / 'app'))).expanduser()
DB_PATH = APP_DATA / 'trustxai.sqlite3'
NLI_THRESHOLD = float(os.environ.get('TRUSTXAI_NLI_THRESHOLD', '0.90'))
if not 0 <= NLI_THRESHOLD <= 1:
    raise ValueError('NLI threshold must lie between zero and one')
MODEL_MEMORY_GIB = 24
TARGET_CONTEXT = 1536
NATIVE_CONTEXT = 4096
BUILD = ROOT / 'frontend/dist'
