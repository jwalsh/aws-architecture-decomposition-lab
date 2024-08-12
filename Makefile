# Diagram Generation
DIAGRAM_SRC_DIR := diagrams-fixed
DIAGRAM_OUT_DIR := docs/images
MERMAID_FILES := $(wildcard $(DIAGRAM_SRC_DIR)/*.mmd)
PNG_DIAGRAMS := $(patsubst $(DIAGRAM_SRC_DIR)/%.mmd,$(DIAGRAM_OUT_DIR)/%.png,$(MERMAID_FILES))
SVG_DIAGRAMS := $(patsubst $(DIAGRAM_SRC_DIR)/%.mmd,$(DIAGRAM_OUT_DIR)/%.svg,$(MERMAID_FILES))
PNG_BG := white # see also transparent
JSON_FILES := $(wildcard *.json)

.PHONY: all diagrams clean prettify-json lint

all: diagrams prettify-json lint


# CI targets
configure:
	@echo "Configuring the project..."
        # Add any necessary configuration steps here

install-deps:
	@echo "Installing dependencies..."

check:
	@echo "Running checks..."

distcheck:
	@echo "Running distribution checks..."


# Generate both PNG and SVG diagrams
diagrams: $(PNG_DIAGRAMS) $(SVG_DIAGRAMS)
	@echo "All diagrams generated successfully."

$(DIAGRAM_OUT_DIR)/%.png: $(DIAGRAM_SRC_DIR)/%.mmd | $(DIAGRAM_OUT_DIR) 
	@echo "Generating PNG diagram: $< -> $@"
	@-mmdc -i $< -o $@ -b $(PNG_BG)

$(DIAGRAM_OUT_DIR)/%.svg: $(DIAGRAM_SRC_DIR)/%.mmd | $(DIAGRAM_OUT_DIR)
	@echo "Generating SVG diagram: $< -> $@"
	@-mmdc -i $< -o $@ -b transparent

$(DIAGRAM_OUT_DIR):
	mkdir -p $@

clean:
	rm -rf $(DIAGRAM_OUT_DIR)


setup-architecture_simulator-db: aws_architecture_seed.sql
	sqlite3 architecture_simulator.db < aws_architecture_seed.sql
	echo "Database initialized!"
	sqlite3 -header -column architecture_simulator.db < aws_architecture_arc_frequency.sql

# Prettify JSON files
prettify-json: $(JSON_FILES)
	@echo "Prettifying JSON files..."
	@for file in $^; do \
		echo "Prettifying $$file"; \
		jq . $$file > $$file.tmp && mv $$file.tmp $$file; \
	done
	@echo "All JSON files prettified successfully."


# Lint all files
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


#  Sync diagrams to projects and README
sync-diagrams-to-projects:
	@echo "Syncing diagrams to projects..."
	@./scripts/sync-diagrams-to-projects.sh

sync-diagrams-to-readme: diagrams
	@echo "Syncing diagrams to README..."
	@./scripts/sync-diagrams-to-readme.sh


# Virtual environments
# .venv: venv

# venv:
# 	@echo "Creating virtual environment..."
# 	@python3 -m venv venv
# 	@echo "Activating virtual environment..."
# 	@source venv/bin/activate
# 	@echo "Installing dependencies..."
# 	@pip install -r requirements.txt
# 	@echo "Virtual environment created successfully."
