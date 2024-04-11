.PHONY: run html_report clean

run:
	pytest -o log_cli=true --log-file=test.log test_tenzor.py

html_report:
	pytest -o log_cli=true --log-file=test.log --html=report.html test_tenzor.py
	xdg-open report.html

clean:
	rm -rf test.log
	rm -rf .pytest_cache
	rm -rf __pycache__
	rm -rf assets
	rm -rf report.html
