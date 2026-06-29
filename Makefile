MYPY_FLAGS  = --warn-return-any \
              --warn-unused-ignores \
              --ignore-missing-imports \
              --disallow-untyped-defs \
              --check-untyped-defs

FLAKE8_EXCLUDE = --exclude=venv
MYPY_EXCLUDE   = --exclude venv

SCRIPT = main.py

all:	install run

install:
	pip install -r requirements.txt

run:
	python3 $(SCRIPT)


debug:
	python3 -m pdb $(SCRIPT)


lint:
	@echo "Comprobando linter..."
	@status=0; \
	echo ""; \
	echo "========== FLAKE8 =========="; \
	uv run flake8 . $(FLAKE8_EXCLUDE) || status=1; \
	echo ""; \
	echo "=========== MYPY ===========" ; \
	uv run mypy . $(MYPY_FLAGS) $(MYPY_EXCLUDE) || status=1; \
	echo ""; \
	exit $$status

lint-strict:
	@echo "Comprobando linter (estricto)..."
	@status=0; \
	echo ""; \
	echo "========== FLAKE8 =========="; \
	uv run flake8 . $(FLAKE8_EXCLUDE) || status=1; \
	echo ""; \
	echo "=========== MYPY ===========" ; \
	uv run mypy . --strict $(MYPY_EXCLUDE) || status=1; \
	echo ""; \
	exit $$status


clean:
	@echo "Cleaning temporary files...\n"

	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

	rm -rf .mypy_cache

	@echo "\nRemoving virtual environment...\n"
	rm -rf .mypy_cache .pytest_cache .ruff_cache
	rm -rf $(VENV)


re: clean all

.PHONY: all venv install run debug lint lint-strict clean re