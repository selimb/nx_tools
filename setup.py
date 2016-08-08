import ast
import os
import re
from setuptools import setup, find_packages
from setuptools.command.bdist_egg import bdist_egg
import shutil
import subprocess


def get_version():
    versionfile = os.path.join('nx_tools', '__main__.py')
    version_re = re.compile(r'__version__\s+=\s+(.*)')
    with open(versionfile, 'r') as f:
        version = str(ast.literal_eval(
                version_re.search(f.read().decode('utf-8')).group(1)
        ))
    return version


version = get_version()
name = 'nx_tools'

ahk2exe = r"C:\Program Files (x86)\AutoHotkey\Compiler\Ahk2Exe.exe"
ahk_scripts = [
    'nx_tools/bin/nx_identifier.ahk',
    'nx_tools/bin/task_update.ahk'
]
ahk_exe = [x.replace('.ahk', '.exe') for x in ahk_scripts]
ahk_cmd = lambda i, o: [ahk2exe, '/in', i, '/out', o]


def compile_AHK():
    for ahk, exe in zip(ahk_scripts, ahk_exe):
        if os.path.exists(exe):
            os.remove(exe)
        cmd = ahk_cmd(ahk, exe)
        print("Compiling %s" % ahk)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        out, err = proc.communicate()
        print(out)


def clean_egg_info():
    shutil.rmtree('%s.egg-info' % name, ignore_errors=True)


class CustomEgg(bdist_egg):
    def run(self):
        compile_AHK()
        bdist_egg.run(self)
        clean_egg_info()

setup(
    author='Selim Belhaouane',
    author_email='selim.belhaouane@gmail.com',
    name=name,
    description=('A command-line utility to automate NX update and launch'),
    license='MIT',
    version=version,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'nx_tools = nx_tools.__main__:nx_tools',
            'nx_tools_utils = nx_tools.__main__:nx_tools_utils'
        ]
    },
    scripts=ahk_exe,
    include_package_data=True,
    install_requires=[
        'click==5.1',
        'pyreadline==2.0'
    ],
    cmdclass={
        'bdist_egg': CustomEgg,
    },
)
