# Diagram Generation
DIAGRAM_SRC_DIR := diagrams
DIAGRAM_OUT_DIR := docs/images
MERMAID_FILES := $(wildcard $(DIAGRAM_SRC_DIR)/*.mmd)
PNG_DIAGRAMS := $(patsubst $(DIAGRAM_SRC_DIR)/%.mmd,$(DIAGRAM_OUT_DIR)/%.png,$(MERMAID_FILES))
SVG_DIAGRAMS := $(patsubst $(DIAGRAM_SRC_DIR)/%.mmd,$(DIAGRAM_OUT_DIR)/%.svg,$(MERMAID_FILES))

# JSON files
JSON_FILES := $(wildcard *.json)

.PHONY: all diagrams clean prettify-json lint

all: diagrams prettify-json lint

# Generate both PNG and SVG diagrams
diagrams: $(PNG_DIAGRAMS) $(SVG_DIAGRAMS)
	@echo "All diagrams generated successfully."

$(DIAGRAM_OUT_DIR)/%.png: $(DIAGRAM_SRC_DIR)/%.mmd | $(DIAGRAM_OUT_DIR)
	@echo "Generating PNG diagram: $< -> $@"
	mmdc -i $< -o $@ -b transparent

$(DIAGRAM_OUT_DIR)/%.svg: $(DIAGRAM_SRC_DIR)/%.mmd | $(DIAGRAM_OUT_DIR)
	@echo "Generating SVG diagram: $< -> $@"
	mmdc -i $< -o $@ -b transparent

$(DIAGRAM_OUT_DIR):
	mkdir -p $@

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

clean:
	rm -rf $(DIAGRAM_OUT_DIR)

## Lint shell scripts
lint-scripts:
	@echo "Linting shell scripts..."
	chmod +x scripts/*.sh
	shfmt -w -s -i 4 scripts/*.sh

## Lint markdown files
lint-markdown:
	@echo "Linting markdown files..."
	@markdownlint --config .markdownlint.json .

sync-diagrams-to-projects:
	@echo "Syncing diagrams to projects..."
	@./scripts/sync-diagrams-to-projects.sh
