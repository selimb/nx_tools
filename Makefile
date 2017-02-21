PY26=/c/Python26/python.exe
ENV=env
env:
	$(PY26) -m virtualenv $(ENV)
	$(ENV)/Scripts/pip install -r dev-requirements.txt
release:
	bash release.sh
test:
	$(ENV)/Scripts/python.exe -m pytest tests

