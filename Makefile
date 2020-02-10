.PHONY: default
default: test lint

test = manage.py test --keepdb

migrations:
	python manage.py makemigrations

test:
	python -Wa $(test)

test/coverage:
	coverage run --branch $(test)

test/coverage/html: test/coverage
	coverage html

lint:
	flake8 .

deps:
	pip install -r requirements.txt

deps/outdated:
	pip list --outdated

deps/update:
	pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U
	pip freeze > requirements.txt
