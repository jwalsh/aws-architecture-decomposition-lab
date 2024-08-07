import json
import os
import requests
from jinja2 import Template
import re
import click

# Optional imports for Ollama, only if needed
try:
    from langchain_community.llms import Ollama
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain.chains.question_answering import load_qa_chain
    from langchain_community.document_loaders import PyPDFLoader
except ImportError:
    # Handle the case where langchain_community is not installed
    pass

# Directory containing the JSON files
directory = '.'

# Template files for org-drill
template_file = 'org-drill-reference-item-template.tmpl'
front_back_template_file = 'org-drill-reference-item-front-back-template.tmpl'

# Output file for org-drill flashcards
output_file = 'aws_reference_architectures_flashcards.org'

# Load the templates
with open(template_file, 'r') as f:
    template_content = f.read()
    template = Template(template_content)

with open(front_back_template_file, 'r') as f:
    front_back_template_content = f.read()
    front_back_template = Template(front_back_template_content)


def download_diagram(url, name, filetype="pdf"):
    """Downloads a diagram if it doesn't exist locally or if --refresh-diagrams is used.

    Args:
        url: The URL of the diagram to download.
        name: The name to use for the saved file.
        filetype: The file extension for the diagram (default: "pdf").
    """

    filename = f"diagrams/{name}.{filetype}"
    if not os.path.exists(filename) or refresh_diagrams:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for bad responses

            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded diagram: {filename}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading diagram for {name}: {e}")
    else:
        print(f"Diagram already exists: {filename}")


def fetch_json_data(page_num):
    """Fetches JSON data from the AWS API for a specific page.

    Args:
        page_num: The page number to fetch.

    Returns:
        The JSON data as a Python dictionary, or None if there's an error.
    """

    url = f"https://aws.amazon.com/api/dirs/items/search?item.directoryId=whitepapers&sort_by=item.additionalFields.sortDate&sort_order=desc&size=9&item.locale=en_US&tags.id=GLOBAL%23content-type%23reference-arch-diagram&page={page_num}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for page {page_num}: {e}")
        return None


def generate_overview(pdf_filename):
    """Generates a high-level overview from the PDF using Ollama.

    Args:
        pdf_filename: The path to the PDF file.

    Returns:
        The generated overview text.
    """

    loader = PyPDFLoader(pdf_filename)
    pages = loader.load_and_split()
    faiss_index = FAISS.from_documents(pages, embeddings)
    chain = load_qa_chain(llm, chain_type="stuff")

    # System prompt for Ollama
    system_prompt = "You're an AWS architect. Provide a high-level overview of the reference architecture mentioned in the attached PDF. Do not indicate the AWS services used."
    query = "What is the high-level overview of this reference architecture?"
    return chain.run(input_documents=faiss_index.similarity_search(query), question=query, system_prompt=system_prompt)

def generate_services_list(text):
    """Generates a list of AWS services mentioned in the text using Ollama.

    Args:
        text: The text to analyze.

    Returns:
        A list of AWS services.
    """

    # System prompt for Ollama
    system_prompt = "You're an AWS architect. List the specific AWS services and technologies mentioned in the following text:"
    query = "What AWS services and technologies are mentioned?"
    return chain.run(input_documents=[text], question=query, system_prompt=system_prompt)

@click.command()
@click.option('--refresh-data', is_flag=True, help='Force re-fetching of JSON data from AWS')
@click.option('--refresh-diagrams', is_flag=True, help='Force re-download of diagrams')
@click.option('--generate-front-back', is_flag=True, help='Generate front and back sections for flashcards using the specified provider')
@click.option('--provider', type=click.Choice(['ollama', 'pdf2text']), default='ollama', help='Provider for generating front/back content (required if --generate-front-back is used)')
def generate_flashcards(refresh_data, refresh_diagrams, generate_front_back, provider):
    """Generates org-drill flashcards from AWS reference architecture JSON files."""

    # Check if --provider is specified when --generate-front-back is used
    if generate_front_back and provider is None:
        raise click.UsageError("--provider is required when using --generate-front-back")

    # Initialize providers (only if needed)
    if generate_front_back and provider == 'ollama':
        llm = Ollama(model="mistral")
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Fetch JSON data if --re-search is used or no JSON files exist
    if refresh_data or not any(f.endswith('.json') for f in os.listdir(directory)):
        for page_num in range(1, 41): 
            filename = f"reference-architecture-diagrams-p{page_num}.json"
            print(f"Fetching Reference Architecture Diagrams page {page_num}")
            data = fetch_json_data(page_num)
            if data:
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=4)

    # Open the output file for writing
    with open(output_file, 'w') as outfile:

        # Iterate through all JSON files in the directory
        for filename in os.listdir(directory):
            if filename.startswith('reference-architecture-diagrams-p') and filename.endswith('.json'):
                with open(os.path.join(directory, filename), 'r') as f:
                    data = json.load(f)

                    # Iterate through items in the JSON data
                    for item in data.get('items', []):
                        item_data = item.get('item', {})
                        additional_fields = item_data.get('additionalFields', {})

                        # Remove HTML tags from the description
                        clean_description = re.sub('<.*?>', '', additional_fields.get('description', ''))

                        # Create a flattened dictionary for the template
                        flattened_data = {
                            'title': additional_fields.get('docTitle', ''),
                            'name': item_data.get('name', ''),
                            'id': item_data.get('id', ''),
                            'created': item_data.get('dateCreated', ''),
                            'url': additional_fields.get('primaryURL', ''),
                            'description': clean_description
                        }

                        if generate_front_back:
                            # Only generate overview and services if --force is used or provider is 'ollama'
                            if force or provider == 'ollama':
                                # Generate overview from PDF or description
                                if os.path.exists(f"diagrams/{item_data.get('name', '')}.pdf"):
                                    overview = generate_overview(f"diagrams/{item_data.get('name', '')}.pdf")
                                else:
                                    overview = clean_description 

                                # Generate services list from description
                                services = generate_services_list(clean_description)

                                # Update flattened_data for the front/back template
                                flattened_data['front'] = overview
                                flattened_data['back'] = services

                                # Render the front/back template
                                rendered_content = front_back_template.render(flattened_data)
                            else:
                                # Use the original template if not forcing overview generation
                                rendered_content = template.render(flattened_data)
                        else:
                            # Use the original template by default
                            rendered_content = template.render(flattened_data)

                        # Write the rendered content to the output file
                        outfile.write(rendered_content)
                        outfile.write('\n')

if __name__ == '__main__':
    generate_flashcards()
