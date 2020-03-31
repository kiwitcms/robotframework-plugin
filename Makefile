.PHONY: flake8
flake8:
	@flake8 --exclude=.git *.py zealand tests

.PHONY: pylint
pylint:
	PYTHONPATH=. pylint --extension-pkg-whitelist=kerberos \
	                    -d missing-docstring -d duplicate-code \
	                    zealand/ tests/

test:
	coverage run --source tcms_api setup.py test

.PHONY: build
build:
	./tests/check-build
