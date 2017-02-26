test:
	pip uninstall -y sphinxcontrib-reviewbuilder && pip install .
	py.test
