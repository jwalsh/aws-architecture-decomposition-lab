# Diagram Generation
DIAGRAM_SRC_DIR := diagrams-fixed
DIAGRAM_OUT_DIR := docs/images
MERMAID_FILES := $(wildcard $(DIAGRAM_SRC_DIR)/*.mmd)
PNG_DIAGRAMS := $(patsubst $(DIAGRAM_SRC_DIR)/%.mmd,$(DIAGRAM_OUT_DIR)/%.png,$(MERMAID_FILES))
SVG_DIAGRAMS := $(patsubst $(DIAGRAM_SRC_DIR)/%.mmd,$(DIAGRAM_OUT_DIR)/%.svg,$(MERMAID_FILES))
ORG_FILES := $(wildcard *.org projects/*/*.org)
PNG_BG := white # see also transparent
JSON_FILES := $(wildcard *.json)

.PHONY: all diagrams clean prettify-json lint

all: diagrams prettify-json lint


# Installation and configuration
install-deps:
	@echo "Installing system dependencies..."
	@sudo apt-get update && sudo apt-get install -y graphviz
	@npm install -g @mermaid-js/mermaid-cli
	@pip install -r requirements.txt

configure:
	@echo "Installing dependencies..."

check:
	@echo "Running checks..."

distcheck:
	@echo "Running distribution checks..."

test:
	@echo "Running tests..."
	@pytest tests/


# Generate both PNG and SVG diagrams
diagrams: $(PNG_DIAGRAMS) $(SVG_DIAGRAMS)
	@echo "All diagrams generated successfully."

$(DIAGRAM_OUT_DIR)/%.png: $(DIAGRAM_SRC_DIR)/%.mmd | $(DIAGRAM_OUT_DIR) 
	@echo "Generating PNG diagram: $< -> $@"
	@-mmdc -i $< -o $@ -b $(PNG_BG)

$(DIAGRAM_OUT_DIR)/%.svg: $(DIAGRAM_SRC_DIR)/%.mmd | $(DIAGRAM_OUT_DIR)
	@echo "Generating SVG diagram: $< -> $@"
	@-mmdc -i $< -o $@

$(DIAGRAM_OUT_DIR):
	@mkdir -p $(DIAGRAM_OUT_DIR)

clean:
	@echo "Cleaning up generated files..."
	@rm -rf $(DIAGRAM_OUT_DIR)

prettify-json:
	@echo "Prettifying JSON files..."
	@for file in $(JSON_FILES); do \
		echo "Prettifying $$file"; \
		prettier --write $$file; \
	done
	@echo "JSON prettification completed."

## Lint Mermaid files
lint:
	@echo "Linting Mermaid files..."
	@for file in $(MERMAID_FILES); do \
		echo "Linting $$file"; \
		mmdc -i $$file -o /dev/null; \
	done
	@echo "Linting completed."


## Lint shell scripts
lint-scripts:
	@echo "Linting shell scripts..."
	chmod +x scripts/*.sh
	shfmt -w -s -i 4 scripts/*.sh

## Lint markdown files
lint-markdown:
	@echo "Linting markdown files..."
	@markdownlint --config .markdownlint.json .

lint-python:
	@echo "Linting Python files..."
	@flake8 .


#  Sync diagrams to projects and README
sync-diagrams-to-projects:
	@echo "Syncing diagrams to projects..."
	@./scripts/sync-diagrams-to-projects.sh

sync-diagrams-to-readme: diagrams
	@echo "Syncing diagrams to README..."
	@./scripts/sync-diagrams-to-readme.sh

# Literate programming
tangle:
	@echo "Tangling org files..."
	@emacs --batch --eval "(require 'org)" --eval '(mapc (lambda (file) (find-file file) (org-babel-tangle) (kill-buffer)) (directory-files-recursively "." "\\.org$"))'

# Virtual environments
venv:
	@echo "Creating virtual environment..."
	@python3 -m venv venv
	@echo "Activating virtual environment..."
	@source venv/bin/activate
	@echo "Installing dependencies..."
	@pip install -r requirements.txt
	@echo "Virtual environment created successfully."

.PHONY: all configure install-deps check distcheck test diagrams prettify-json lint lint-scripts lint-markdown lint-python sync-diagrams-to-projects sync-diagrams-to-readme tangle venv
