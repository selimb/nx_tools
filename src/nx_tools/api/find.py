import os


UGRAF_EXE = 'ugraf.exe'


def ugraf(nx_root):
    print nx_root
    print os.listdir(nx_root)
    for dirpath, dirnames, filenames in os.walk(nx_root):
        print dirpath
        print filenames
        if UGRAF_EXE in filenames:
            return os.path.join(dirpath, UGRAF_EXE)

    return None


def tmg(tmg_root):
    raise NotImplementedError

