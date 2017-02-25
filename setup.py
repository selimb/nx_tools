import ast
import os
import re
import shutil
import subprocess

from setuptools import Command, find_packages, setup

SRC = 'src'
name = 'nx_tools'

ahk2exe = os.path.join('C:\\', 'Program Files (x86)', 'AutoHotkey', 'Compiler', 'Ahk2Exe.exe')
# ahk2exe = r'C:\Program Files (x86)\AutoHotkey\Compiler\Ahk2Exe.exe'
bin_dir = os.path.join(SRC, name, 'bin')
ahk_scripts = [
    os.path.join(bin_dir, 'nx_identifier.ahk'),
    os.path.join(bin_dir, 'task_update.ahk')
]
ahk_exe = [x.replace('.ahk', '.exe') for x in ahk_scripts]
ahk_cmd = lambda i, o: [ahk2exe, '/in', i, '/out', o]


class AHKCompiler(Command):
    user_options = []
    boolean_options = []
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        assert os.path.exists(ahk2exe)
        for ahk, exe in zip(ahk_scripts, ahk_exe):
            if os.path.exists(exe):
                os.remove(exe)
            print 'Compiling %s' % ahk
            assert os.path.exists(ahk)
            cmd = ahk_cmd(ahk, exe)
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            out, err = proc.communicate()
            print out


setup(
    name=name,
    version='1.10.0',
    license='MIT',
    description='A command-line utility to automate NX update and launch',
    author='Selim Belhaouane',
    author_email='selim.belhaouane@gmail.com',
    url='https://github.com/selimb/nx_tools',
    packages=find_packages(SRC),
    package_dir={'': SRC},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'nx_tools = nx_tools.__main__:nx_tools',
            'nx_tools_utils = nx_tools.__main__:nx_tools_utils'
        ]
    },
    install_requires=[
        'click==5.1',
        'pyreadline==2.0'
    ],
    cmdclass={
        'ahk': AHKCompiler
    }
)
