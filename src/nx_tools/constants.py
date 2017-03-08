import os

from pkg_resources import resource_filename, Requirement

# NOTE: Paths refering to PKG are relative to the location of this file (constants.py).
PKG = resource_filename('nx_tools', '')
PKG_DATA = os.path.join(PKG, 'data')
PKG_BIN = os.path.join(PKG, 'bin')
DEFAULT_CONFIG_PATH = os.path.join(PKG_DATA, 'default_config.json')

USER_ROOT = os.path.join('D:\\', '.nx_tools')
USER_CONFIG_PATH = os.path.join(USER_ROOT, 'nx_tools.json')

# History
HISTORY_PATH = os.path.join(USER_ROOT, 'history.json')
HISTORY_MAX_RECORDS = 20

NPP = r"C:\Program Files (x86)\Notepad++\notepad++.exe"
