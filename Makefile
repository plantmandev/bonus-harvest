PYTHON  := python3
VENV    := .venv
PIP     := $(VENV)/bin/pip
PROJECT := $(shell pwd)

.DEFAULT_GOAL := install

.PHONY: install run clean

install: $(VENV)/bin/activate
	@git config core.hooksPath .githooks
	@echo "Setup complete. Activate with: source .venv/bin/activate"

$(VENV)/bin/activate: requirements.txt
	$(PYTHON) -m venv $(VENV)
	$(PIP) install -q --upgrade pip
	$(PIP) install -q -r requirements.txt
	@touch $(VENV)/bin/activate

run:
	bash scripts/run_all.sh

clean:
	rm -rf $(VENV)
