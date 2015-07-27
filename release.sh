#!/usr/bin/env bash
py26="/cygdrive/c/Python26/python.exe"
echo Getting version
package_version=$($py26 -c "from nx_tools import __version__; print __version__")
setup_version=$($py26 setup.py --version)
if [ $package_version != $setup_version ] ; then
	echo FATAL
	echo "Setup.py version $setup_version != Package version $package_version"
	return
fi
version=$setup_version
echo Version=$version
echo Did you update CHANGELOG.md?
echo Did you commit your changes?
read -p "Press any key to start release"

echo ''
echo Building
echo =======
$py26 setup.py bdist_egg

echo ''
echo Rolling out
echo ==========
dest="/cygdrive/t/selimb/nx_tools"
echo Syncing opt/
rsync -r --del opt/ $dest
echo Echoing version number
echo $version > $dest/version.txt
