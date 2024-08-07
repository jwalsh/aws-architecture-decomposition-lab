import json
import os
import requests
from jinja2 import Template
import re
import click
import subprocess
from pdf2image import convert_from_path

# Directory containing the JSON files
directory = '.'

# Template files for org-drill
remote_template_file = 'org-drill-remote-template.tmpl'
local_template_file = 'org-drill-local-template.tmpl'
ai_enhanced_template_file = 'org-drill-ai-enhanced-template.tmpl'

# Output file for org-drill flashcards
output_file = 'aws-reference-architectures-drill.org'

# Load the templates
# Load the templates
with open(remote_template_file, 'r') as f:
    remote_template_content = f.read()
    remote_template = Template(remote_template_content)

with open(local_template_file, 'r') as f:
    local_template_content = f.read()
    local_template = Template(local_template_content)

def clean_text(text):
    """
    Clean the input text by removing special characters and extra whitespace.
    """
    # Remove carriage returns, newlines, and tabs
    text = re.sub(r'[\r\n\t]+', ' ', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    # Strip leading and trailing whitespace
    text = text.strip()
    return text

def ensure_diagrams_directory():
    """Creates the 'diagrams' directory if it doesn't exist."""
    if not os.path.exists('diagrams'):
        os.makedirs('diagrams')
        print("Created 'diagrams' directory.")

def download_diagram(url, name, filetype="pdf", refresh=False):
    """Downloads a diagram if it doesn't exist locally or if refresh is True."""
    ensure_diagrams_directory()
    filename = f"diagrams/{name}.{filetype}"
    
    if not os.path.exists(filename) or refresh:
        try:
            response = requests.get(url)
            response.raise_for_status()
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded diagram: {filename}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading diagram for {name}: {e}")
    else:
        print(f"Diagram already exists: {filename}")

def fetch_json_data(page_num):
    """Fetches JSON data from the AWS API for a specific page."""
    url = f"https://aws.amazon.com/api/dirs/items/search?item.directoryId=whitepapers&sort_by=item.additionalFields.sortDate&sort_order=desc&size=9&item.locale=en_US&tags.id=GLOBAL%23content-type%23reference-arch-diagram&page={page_num}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for page {page_num}: {e}")
        return None

def process_tags(tags):
    """Process tags to extract tech categories and other relevant tags."""
    tech_tags = []
    for tag in tags:
        tag_parts = tag['id'].split('#')
        if len(tag_parts) > 2:
            tag_name = tag_parts[-1]
            if tag_parts[1] == 'tech-category':
                tech_tags.append(tag_name)
    return ':drill:' + ':'.join(tech_tags) + ':' if tech_tags else ':drill:'

def convert_pdf_to_image(pdf_path, output_path):
    """Convert PDF to image using pdf2image."""
    try:
        images = convert_from_path(pdf_path, dpi=150, first_page=1, last_page=1)
        if images:
            images[0].save(output_path, 'PNG')
            print(f"Converted {pdf_path} to {output_path}")
            return True
    except Exception as e:
        print(f"Error converting {pdf_path} to image: {e}")
    return False

def process_diagram(url, name, refresh=False):
    """Process diagram: download if needed, convert to image if possible."""
    pdf_filename = f"diagrams/{name}.pdf"
    image_filename = f"diagrams/{name}.png"
    
    # Download PDF if it doesn't exist or refresh is True
    if not os.path.exists(pdf_filename) or refresh:
        download_diagram(url, name, refresh=refresh)
    
    # Convert PDF to image if PDF exists and image doesn't exist or refresh is True
    if os.path.exists(pdf_filename) and (not os.path.exists(image_filename) or refresh):
        convert_pdf_to_image(pdf_filename, image_filename)
    
    # Return the appropriate filename to use in the flashcard
    if os.path.exists(image_filename):
        return f"[[file:{image_filename}]]"
    elif os.path.exists(pdf_filename):
        return f"[[file:{pdf_filename}]]"
    else:
        return None

@click.command()
@click.option('--refresh-data', is_flag=True, help='Force re-fetching of JSON data from AWS')
@click.option('--refresh-diagrams', is_flag=True, help='Force re-download of diagrams')
@click.option('--local-pdf', is_flag=True, help='Use local PDF links instead of URLs')
@click.option('--ai-generate', is_flag=True, help='Generate AI-enhanced content for flashcards')
@click.option('--ai-provider', type=click.Choice(['ollama', 'claude', 'openai', 'gemini']), 
              default='ollama', help='AI provider for generating enhanced content (if --ai-generate is used)')
def generate_flashcards(refresh_data, refresh_diagrams, local_pdf, ai_generate, ai_provider):
    """Generates org-drill flashcards from AWS reference architecture JSON files."""

    # Fetch JSON data if --refresh-data is used or no JSON files exist
    if refresh_data or not any(f.startswith('reference-architecture-diagrams-p') and f.endswith('.json') for f in os.listdir(directory)):
        for page_num in range(1, 41):  # Assuming up to 40 pages
            filename = f"reference-architecture-diagrams-p{page_num}.json"
            print(f"Fetching Reference Architecture Diagrams page {page_num}")
            data = fetch_json_data(page_num)
            if data:
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=4)
            else:
                break  # Stop if we get no data (likely reached the end of pages)

    # Open the output file for writing
    with open(output_file, 'w') as outfile:
        # Iterate through all JSON files in the directory
        for filename in sorted(os.listdir(directory)):
            if filename.startswith('reference-architecture-diagrams-p') and filename.endswith('.json'):
                with open(os.path.join(directory, filename), 'r') as f:
                    data = json.load(f)

                    # Iterate through items in the JSON data
                    for item in data.get('items', []):
                        item_data = item.get('item', {})
                        additional_fields = item_data.get('additionalFields', {})

                        # Remove HTML tags from the description
                        clean_description = clean_text(re.sub('<.*?>', '', additional_fields.get('description', '')))

                        # Process tags
                        tags = process_tags(item.get('tags', []))

                        # Determine the URL or local file link
                        name = item_data.get('name', '')
                        url = additional_fields.get('primaryURL', '')

                        # Create a flattened dictionary for the template
                        flattened_data = {
                            'docTitle': clean_text(additional_fields.get('docTitle', '')),
                            'tags': tags,
                            'id': item_data.get('id', ''),
                            'dateCreated': item_data.get('dateCreated', ''),
                            'primaryURL': url,
                            'description': clean_description
                        }

                        if local_pdf:
                            download_diagram(url, name, refresh=refresh_diagrams)
                            link = process_diagram(url, name, refresh=refresh_diagrams)
                            flattened_data['link'] = link
                        else:
                            flattened_data['link'] = f"[[{url}]]"
                            rendered_content = remote_template.render(flattened_data)

                        # Write the rendered content to the output file
                        outfile.write(rendered_content)
                        outfile.write('\n')

    print(f"Flashcards generated in {output_file}")

if __name__ == '__main__':
    generate_flashcards()
