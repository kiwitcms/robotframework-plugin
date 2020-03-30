.PHONY: flake8
flake8:
	@flake8 --exclude=.git *.py zealand tests

.PHONY: pylint
pylint:
	PYTHONPATH=. pylint -d missing-docstring *.py zealand/ tests/

test:
	coverage run --source tcms_api setup.py test

.PHONY: doc8
doc8:
	doc8 README.rst

.PHONY: build
build:
	./tests/check-build

.PHONY: integration_test
integration_test:
	if [ -z $$(which geckodriver) ]; then \
	    pip install -q -U webdrivermanager; \
	    sudo webdrivermanager firefox --linkpath /usr/local/bin; \
	fi

	[ -d WebDemo ] || git clone --depth=1 https://github.com/robotframework/WebDemo.git

	pip install -q -U -r WebDemo/requirements.txt
	# demo web app is running at http://localhost:7272
	python WebDemo/demoapp/server.py >/dev/null 2>&1 &

	@sleep 2
	PYTHONPATH=. robot --listener zealand.listener.KiwiTCMS -d WebDemo/ WebDemo/login_tests/
	@killall -9 -q -u $$(whoami) python
