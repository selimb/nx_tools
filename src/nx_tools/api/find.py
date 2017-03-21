import os


UGRAF_EXE = 'ugraf.exe'


def ugraf(nx_root):
    for dirpath, dirnames, filenames in os.walk(nx_root):
        if UGRAF_EXE in filenames:
            return os.path.join(dirpath, UGRAF_EXE)

    return None


def tmg(tmg_root):
    for dirpath, dirnames, filenames in os.walk(tmg_root):
        monitor = os.path.join(dirpath, 'exe', 'MayaMonitor.exe')
        if os.path.exists(monitor):
            return dirpath

    return None

