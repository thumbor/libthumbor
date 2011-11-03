test:
	nosetests -v -s tests

publish:
	python setup.py sdist upload
