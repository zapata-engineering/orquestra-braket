################################################################################
# © Copyright 2022 Zapata Computing Inc.
################################################################################
include subtrees/z_quantum_actions/Makefile

github_actions:
	python3 -m venv my_little_venv && \
		my_little_venv/bin/python3 -m pip install --upgrade pip && \
		my_little_venv/bin/python3 -m pip install -e orquestra-quantum && \
		my_little_venv/bin/python3 -m pip install -e '.[dev]'


ondemandcoverage:
	$(PYTHON) -m pytest -m cloud \
		--cov=src \
		--cov-fail-under=$(MIN_COVERAGE) tests\
		--no-cov-on-fail \
		--cov-report xml \
		&& echo Code coverage Passed the $(MIN_COVERAGE)% mark!

coverage:
	$(PYTHON) -m pytest -m local \
		--cov=src \
		--cov-fail-under=$(MIN_COVERAGE) tests\
		--no-cov-on-fail \
		--cov-report xml \
		&& echo Code coverage Passed the $(MIN_COVERAGE)% mark!

totalcoverage:
	$(PYTHON) -m pytest -m "local or cloud"\
		--cov=src \
		--cov-fail-under=$(MIN_COVERAGE) tests\
		--no-cov-on-fail \
		--cov-report xml \
		&& echo Code coverage Passed the $(MIN_COVERAGE)% mark!
