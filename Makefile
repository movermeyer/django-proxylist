test:
	django-admin.py test --settings=proxylist.test_settings proxylist

coverage:
	export DJANGO_SETTINGS_MODULE=proxylist.test_settings && \
	coverage run --branch --source=proxylist `which django-admin.py` test proxylist && \
	coverage report --omit="proxylist/test*,proxylist/migrations/*,proxylist/management/*"

pep8:
	flake8 --exclude=migrations --ignore="W801,W402,F401" proxylist

sphinx:
	cd docs && sphinx-build -b html -d .build/doctrees . .build/html

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

release: clean
	python setup.py register sdist upload --sign
	python setup.py bdist_wheel upload --sign
