test:
	nosetests -v -s tests

ci_test:
	nosetests -v -s tests

publish:
	python setup.py sdist upload
