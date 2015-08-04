import os
from setuptools import setup, find_packages
from setuptools.command.bdist_egg import bdist_egg
import shutil
import subprocess

version = '1.1.6'
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
        'click>=4.0',
        'pyreadline==2.0'
    ],
    cmdclass={
        'bdist_egg': CustomEgg,
    },
)
