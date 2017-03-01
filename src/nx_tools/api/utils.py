import logging
import os
import json

logger = logging.getLogger(__name__)


def load_json(filepath):
    s = open(filepath).read().replace('\\', '\\\\')
    minified = ''
    for line in s.split('\n'):
        if line.strip().startswith('//'):
            continue
        minified += line + '\n'
    return json.loads(minified)


def write_json(obj, filepath):
    ensure_dir_exists(os.path.dirname(filepath))
    with open(filepath, 'w') as f:
        json.dump(obj, f, separators=(',', ':'), indent=4)


def ensure_dir_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.debug('Ensured %s exists.' % directory)


def get_filename(filepath):
    basename = os.path.basename(filepath)
    filename, ext = os.path.splitext(basename)
    return filename
