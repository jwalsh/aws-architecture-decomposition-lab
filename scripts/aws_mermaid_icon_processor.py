import json
import re
from typing import Dict
import click


def example() -> None:
    """
    Main function to demonstrate the usage of the AWS Mermaid icon processor.
    """
    # Example Mermaid diagram
    input_diagram = '''
    graph TD
        user([User])
        route53:dns[DNS]
        cloudfront:cdn[CDN]
        apigateway:api[API Gateway]
        lambda:auth[Auth Function]
        lambda:process[Process Function]
        dynamodb:users[Users Table]
        s3:assets[Asset Storage]
        
        user --> route53:dns
        route53:dns --> cloudfront:cdn
        cloudfront:cdn --> apigateway:api
        apigateway:api --> lambda:auth
        apigateway:api --> lambda:process
        lambda:auth --> dynamodb:users
        lambda:process --> s3:assets
    '''

    # Load the AWS icons mapping
    icons_mapping = load_icons_mapping('aws_icons_mapping.json')

    # Process the diagram
    output_diagram = add_icons_to_mermaid(input_diagram, icons_mapping)

    # Print the result
    print(output_diagram)

def load_icons_mapping(file_path: str) -> Dict[str, str]:
    """Load the AWS icons mapping from a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def add_icons_to_mermaid(mermaid_diagram: str, icons_mapping: Dict[str, str]) -> str:
    """Add AWS service icons to a Mermaid diagram."""
    lines = mermaid_diagram.split('\n')
    modified_lines = []

    for line in lines:
        match = re.match(r'^\s*(\w+(?:[:_]\w+)?)\s*\[(.*?)\]', line)
        if match:
            full_node_name = match.group(1)
            node_label = match.group(2)
            
            node_parts = re.split(r'[:_]', full_node_name)
            service_name = node_parts[0].lower()
            
            if service_name in icons_mapping:
                icon_url = icons_mapping[service_name]
                modified_line = f"{full_node_name}[<img src='{icon_url}' width='48' height='48' /><br>{node_label}]"
                modified_lines.append(modified_line)
            else:
                modified_lines.append(line)
        else:
            modified_lines.append(line)

    return '\n'.join(modified_lines)

@click.command()
@click.argument('input_file', type=click.File('r'))
@click.argument('output_file', type=click.File('w'))
@click.option('--icons', default='aws_icons_mapping.json', help='AWS icons mapping file', type=click.Path(exists=True))
def main(input_file, output_file, icons):
    """Process a Mermaid diagram file and add AWS service icons."""
    click.echo(f"Processing {input_file.name} with icons from {icons}")
    
    input_diagram = input_file.read()
    icons_mapping = load_icons_mapping(icons)
    
    output_diagram = add_icons_to_mermaid(input_diagram, icons_mapping)
    
    output_file.write(output_diagram)
    click.echo(f"Processed diagram written to {output_file.name}")

if __name__ == "__main__":
    main()
