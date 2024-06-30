#!/usr/bin/env bash

# Script to validate Mermaid diagrams and their corresponding projects

# Utility functions

warn() {
    # Show warning icon and message in red color
    echo -e "\033[31m⚠️ $@\033[0m" 1>&2

}

info() {
    # Show info icon and message in blue color
    echo -e "\033[34m🔵 $@\033[0m" 1>&2
}

pass() {
    # Show success icon and message in green color
    echo -e "\033[32m✅ $@\033[0m" 1>&2
}

error() {
    # Show error icon and message in red color
    echo -e "\033[31m❌ $@\033[0m" 1>&2
}

# Configuration (Optional)
diagrams_dir="diagrams" # Directory containing Mermaid diagrams
projects_dir="projects" # Directory containing project folders

# Function to validate a Mermaid diagram
validate_diagram() {
    local diagram="$1"
    mmdc -v "$diagram" >/dev/null 2>&1 # Validate diagram, redirect output to /dev/null
    if [[ $? -ne 0 ]]; then
        return 1
    fi
}

# Function to check if a project directory exists
check_project() {
    local diagram="$1"
    local project_name="${diagram##*/}" # Extract filename without path
    project_name="${project_name%.mmd}" # Remove .mmd extension
    if [[ ! -d "$projects_dir/$project_name" ]]; then
        return 1
    fi
}

add_project() {
    #
    local diagram="$1"
    local project_name="${diagram##*/}"               # Extract filename without path
    project_name="${project_name%.mmd}"               # Remove .mmd extension
    project_name=$(echo "$project_name" | tr '_' '-') # Change underscore to dash

    if [[ ! -d "$projects_dir/$project_name" ]]; then
        mkdir "$projects_dir/$project_name"
        pass "Project $project_name created"
    else
        warn "Project $project_name already exists"
    fi

    # Add a README.org file to the project directory
    cat >"$projects_dir/$project_name/README.org" <<EOF

#+TITLE: $project_name
#+DESCRIPTION: Project for Mermaid diagram $diagram
EOF

}

# Main script execution
echo "Validating Mermaid diagrams and checking for corresponding projects..."

for diagram in "$diagrams_dir"/*.mmd; do
    info "Validating $diagram..."
    errors=0
    if ! validate_diagram "$diagram"; then
        errors=$((errors + 1))
        warn "$diagram is not a valid Mermaid diagram"
    fi

    if ! check_project "$diagram"; then
        errors=$((errors + 1))
        warn "Project for $diagram does not exist"
        add_project "$diagram"
    fi

    if [[ $errors -eq 0 ]]; then
        pass "$diagram is valid and project exists"
    fi
done

echo "All Mermaid diagrams are valid and corresponding projects exist!"
