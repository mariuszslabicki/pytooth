build_venv: requirements-to-freeze.txt
	rm -rf .venv/
	test -f .venv/bin/activate || virtualenv -p $(shell which python3) .venv
	. .venv/bin/activate ;\
	pip install -Ur requirements-to-freeze.txt ;\
	pip freeze | sort > requirements.txt
	touch .venv/bin/activate

.PHONY: run
run: .venv/bin/activate
	. .venv/bin/activate ; \
	python3 run.py