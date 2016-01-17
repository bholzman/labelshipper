default: dirs test

test:
	PYTHONPATH=.:$PYTHONPATH /usr/local/bin/python /usr/local/share/python/py.test -v tests

ci:
	while sleep 5; do /usr/local/share/python/pyflakes .; make test; done

dirs:
	mkdir -p reports/ pdfs/
