import os
import pkg_resources

PKG = pkg_resources.resource_filename(__name__, '')
PKG_DATA = os.path.join(PKG, 'data')
PKG_BIN = os.path.join(PKG, 'bin')
DEFAULT_CONFIG_PATH = os.path.join(PKG_DATA, 'default_config.json')

USER_ROOT = os.path.join('D:\\', '.nx_tools')
USER_CONFIG_PATH = os.path.join(USER_ROOT, 'nx_tools.json')

# History
HISTORY_PATH = os.path.join(USER_ROOT, 'history.json')
HISTORY_MAX_RECORDS = 20

NPP = r"C:\Program Files (x86)\Notepad++\notepad++.exe"