VENV = venv
PYTHON = $(venv)/bin/python3
PIP = $(venv)/bin/pip

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt

clean:
	find . -name __pycache__ -exec rm -rf {} +
	rm -rf $(VENV)
	rm -rf *.egg-info
	rm -rf .virtualenv
