.PHONY: test

test:
	python3 -m pytest -xv --flake8 --pylint --mypy tests/bundler_test.py
