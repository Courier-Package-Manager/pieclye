VENV = venv
PYTHON = $(venv)/bin/python3
PIP = $(venv)/bin/pip


run: $(VENV)/bin/activate
	$(PYTHON) __main__.py


$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt


clean:
	rm -rf __pycache__
	rm -rf $(VENV)
