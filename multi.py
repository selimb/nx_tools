# from multiprocessing.pool import ThreadPool
from multiprocessing import Pool as ThreadPool
import os
import subprocess
import shutil
from time import time
import sys

fname = 'patch.7z'
# fname = 'kits_minimal_.7z'
# fname = 'hello.txt'
root, ext = os.path.splitext(fname)
# SRC_DIR = os.path.abspath('src')
SRC_DIR = 'src'
# DEST_DIR = os.path.abspath('dest')
DEST_DIR = 'dest'

def cp(i):
    ti0 = time()
    src = os.path.join(SRC_DIR, '%s%i%s' % (root, i, ext))
    if not os.path.exists(src):
        print 'ERROR: %s does not exist.' % src
        return

    # print 'Copying %s' % src
    shutil.copy(src, DEST_DIR)
    ti1 = time()
    # print 'Copying %s took %s' % (i, ti1-ti0)
    return i

def extract(i):
    # exe = "C:\\Program Files\\7-Zip\\7zG.exe"
    ti0 = time()
    src = SRC_DIR + '\\' + '%s%i%s' % (root, i, ext)
    # src = os.path.join(SRC_DIR, '%s%i%s' % (root, i, ext))
    if not os.path.exists(src):
        print 'ERROR: %s does not exist.' % src
        return

    dest = DEST_DIR + '\\' + '%s%i' % (root, i)
    print 'Extracting %s' % src
    command = [exe, 'x', src, '-o' + dest]
    p = subprocess.Popen(command)
    p.wait()
    ti1 = time()
    print 'Extracting %s took %s' % (i, ti1-ti0)

def main():
    if os.path.exists(DEST_DIR):
        shutil.rmtree(DEST_DIR)

    os.mkdir(DEST_DIR)

    exe = os.path.join('C:\\', 'Program Files', '7-Zip', '7zG.exe')
    print 'exe: ', exe


    try:
        argv = sys.argv[1]
    except IndexError:
        argv = ''

    t0 = time()
    if argv == 'multi':
        print 'Running multi'
        pool = ThreadPool(3)
        f = pool.map
    else:
        print 'Running single'
        f = map

# f(cp, reversed(range(3)))
# f(extract, range(3))
    imap = pool.imap_unordered(cp, reversed(range(3)))
    for i in imap:
        print i

    t1 = time()
    print 'Took %s' % (t1 - t0)

if __name__ == '__main__':
    main()
