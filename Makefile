# The documentation of Slabs: the hub at the root of the site, one directory per project and per version.
# "make install" once, "make serve p=<project> v=<version>" to write, "make check" before a pull request.

VENV := .venv
BIN := $(VENV)/bin
UV := $(shell command -v uv 2>/dev/null)

# News about the MkDocs ecosystem, not findings about this site. requirements.txt pins the 1.x line.
export NO_MKDOCS_2_WARNING := true
export DISABLE_MKDOCS_2_WARNING := true

.DEFAULT_GOAL := help
.PHONY: help install serve build check projects clean

help: ## Show this help
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

$(BIN)/mkdocs: requirements.txt
ifdef UV
	uv venv --allow-existing $(VENV)
	VIRTUAL_ENV=$(VENV) uv pip install -r requirements.txt
else
	python3 -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt
endif
	@touch $(BIN)/mkdocs

install: $(BIN)/mkdocs ## Install the toolchain in .venv

projects: ## List what can be served
	@ls -d projects/*/*/ | sed 's|projects/||;s|/$$||;s|/| |' | awk '{printf "  p=%-10s v=%s\n", $$1, $$2}'

# Without p= and v=, the hub. With them, that version of that project, on its own.
serve: install ## Serve on http://127.0.0.1:8000 — make serve p=jwt v=4.3
	$(BIN)/python -I tools/build.py --sync-shared
ifdef p
	$(BIN)/mkdocs serve -f projects/$(p)/$(v)/mkdocs.yml
else
	$(BIN)/mkdocs serve -f mkdocs.yml
endif

build: install ## Build the whole site into site/
	$(BIN)/python -I tools/build.py

check: install ## Build the whole site strictly: a broken link or a page outside the navigation fails
	$(BIN)/python -I tools/build.py --strict

clean: ## Remove the build and the virtual environment
	rm -rf site $(VENV)
