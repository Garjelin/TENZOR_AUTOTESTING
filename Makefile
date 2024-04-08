.PHONY: run clean

run:
	pytest -o log_cli=true --log-file=test.log test_tenzor.py

clean:
	rm -f test.log
	rm -rf .pytest_cache
	rm -rf __pycache__
