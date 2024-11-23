.PHONY: install run test clean

install:
	pip install -r requirements.txt

run:
	python run.py

test:
	pytest tests/

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete