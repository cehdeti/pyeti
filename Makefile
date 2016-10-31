test = -m unittest discover "tests" "test_*.py"

init:
	pip install -r requirements.txt

test:
	python $(test)

coverage:
	coverage run $(test)

coverage_html: coverage
	coverage html

lint:
	pep8 .
