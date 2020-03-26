.PHONY: flake8
flake8:
	@flake8 --exclude=.git *.py tcms_api tests

.PHONY: pylint
pylint:
	PYTHONPATH=. pylint --extension-pkg-whitelist=kerberos \
	                    -d missing-docstring -d duplicate-code \
	                    tcms_api/ tests/

test:
	coverage run --source tcms_api setup.py test

.PHONY: build
build:
	./tests/check-build
