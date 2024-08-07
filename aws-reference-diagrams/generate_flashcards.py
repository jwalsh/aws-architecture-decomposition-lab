import json
import os
import requests
from jinja2 import Template
import re
import click

# Directory containing the JSON files
directory = '.'

# Template files for org-drill
template_file = 'org-drill-reference-item-template.tmpl'
front_back_template_file = 'org-drill-reference-item-front-back-template.tmpl'

# Output file for org-drill flashcards
output_file = 'aws-reference-architectures-drill.org'

# Load the templates
with open(template_file, 'r') as f:
    template_content = f.read()
    template = Template(template_content)

with open(front_back_template_file, 'r') as f:
    front_back_template_content = f.read()
    front_back_template = Template(front_back_template_content)

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

@click.command()
@click.option('--refresh-data', is_flag=True, help='Force re-fetching of JSON data from AWS')
@click.option('--refresh-diagrams', is_flag=True, help='Force re-download of diagrams')
@click.option('--generate-front-back', is_flag=True, help='Generate front and back sections for flashcards')
@click.option('--provider', type=click.Choice(['pdf2text', 'ollama', 'claude', 'openai', 'gemini']), 
              default='pdf2text', help='Provider for generating front/back content (if --generate-front-back is used)')
@click.option('--local-pdf', is_flag=True, help='Use local PDF links instead of URLs')
def generate_flashcards(refresh_data, refresh_diagrams, generate_front_back, provider, local_pdf):
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
                        if local_pdf:
                            link = f"[[./diagrams/{name}.pdf]]"
                        else:
                            link = url

                        # Create a flattened dictionary for the template
                        flattened_data = {
                            'docTitle': clean_text(additional_fields.get('docTitle', '')),
                            'tags': tags,
                            'id': item_data.get('id', ''),
                            'dateCreated': item_data.get('dateCreated', ''),
                            'primaryURL': link,
                            'description': clean_description
                        }

                        # Download the diagram
                        download_diagram(url, name, refresh=refresh_diagrams)

                        # Use the original template (without front/back processing)
                        rendered_content = template.render(flattened_data)

                        # Write the rendered content to the output file
                        outfile.write(rendered_content)
                        outfile.write('\n')

    print(f"Flashcards generated in {output_file}")

if __name__ == '__main__':
    generate_flashcards()
