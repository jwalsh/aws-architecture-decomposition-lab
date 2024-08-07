import json
import re
from typing import Dict, List

def load_icons_mapping(file_path: str) -> Dict[str, str]:
    """
    Load the AWS icons mapping from a JSON file.

    Args:
        file_path (str): Path to the JSON file containing the icons mapping.

    Returns:
        Dict[str, str]: A dictionary mapping AWS service names to their icon URLs.
    """
    with open(file_path, 'r') as f:
        return json.load(f)

def add_icons_to_mermaid(mermaid_diagram: str, icons_mapping: Dict[str, str]) -> str:
    """
    Add AWS service icons to a Mermaid diagram.

    This function processes a Mermaid diagram and adds AWS service icons to nodes
    that have a matching prefix in the icons_mapping.

    Args:
        mermaid_diagram (str): The input Mermaid diagram as a string.
        icons_mapping (Dict[str, str]): A dictionary mapping AWS service names to their icon URLs.

    Returns:
        str: The modified Mermaid diagram with AWS service icons added.

    Example:
        >>> mermaid_diagram = '''
        ... graph TD
        ...     user([User])
        ...     route53:dns[DNS]
        ...     cloudfront:cdn[CDN]
        ...     apigateway:api[API Gateway]
        ...     lambda:auth[Auth Function]
        ...     lambda:process[Process Function]
        ...     dynamodb:users[Users Table]
        ...     s3:assets[Asset Storage]
        ...     
        ...     user --> route53:dns
        ...     route53:dns --> cloudfront:cdn
        ...     cloudfront:cdn --> apigateway:api
        ...     apigateway:api --> lambda:auth
        ...     apigateway:api --> lambda:process
        ...     lambda:auth --> dynamodb:users
        ...     lambda:process --> s3:assets
        ... '''
        >>> icons_mapping = load_icons_mapping('aws_icons_mapping.json')
        >>> result = add_icons_to_mermaid(mermaid_diagram, icons_mapping)
        >>> print(result)
    """
    lines: List[str] = mermaid_diagram.split('\n')
    modified_lines: List[str] = []

    for line in lines:
        # Check if the line defines a node
        match = re.match(r'^\s*(\w+(?:[:_]\w+)?)\s*\[(.*?)\]', line)
        if match:
            full_node_name = match.group(1)
            node_label = match.group(2)
            
            # Split the node name to get the service prefix
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

def main() -> None:
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

if __name__ == "__main__":
    main()
