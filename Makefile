.PHONY: default
default: init test lint

test = manage.py test --keepdb

init:
	pip install -r requirements.txt

migrations:
	python manage.py makemigrations

test:
	python -Wa $(test)

coverage:
	coverage run --branch $(test)

coverage_html: coverage
	coverage html

lint:
	flake8 .
