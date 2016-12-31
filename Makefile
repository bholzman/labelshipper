default: dirs test

test:
	PYTHONPATH=.:$(PYTHONPATH) /usr/local/bin/pytest -v tests

ci:
	while true; do flake8 . && make test; sleep 1; done

dirs:
	mkdir -p reports/ pdfs/
