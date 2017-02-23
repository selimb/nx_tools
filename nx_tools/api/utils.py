import logging
import os


logger = logging.getLogger(__name__)


def ensure_dir_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.debug('Ensured %s exists.' % directory)


def get_filename(filepath):
    basename = os.path.basename(filepath)
    filename, ext = os.path.splitext(basename)
    return filename
