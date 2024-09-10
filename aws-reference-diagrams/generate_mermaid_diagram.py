import json
import re
from typing import Dict, List, Tuple
import click
import boto3
from botocore.exceptions import ClientError

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

def mine_aws_data() -> Tuple[List[str], List[Tuple[str, str]]]:
    """Mine data from AWS to get resources and their connections."""
    resources = []
    connections = []
    
    # Initialize AWS clients
    ec2 = boto3.client('ec2')
    s3 = boto3.client('s3')
    lambda_client = boto3.client('lambda')
    
    try:
        # Get EC2 instances
        ec2_response = ec2.describe_instances()
        for reservation in ec2_response['Reservations']:
            for instance in reservation['Instances']:
                resources.append(f"ec2:{instance['InstanceId']}")
        
        # Get S3 buckets
        s3_response = s3.list_buckets()
        for bucket in s3_response['Buckets']:
            resources.append(f"s3:{bucket['Name']}")
        
        # Get Lambda functions
        lambda_response = lambda_client.list_functions()
        for function in lambda_response['Functions']:
            resources.append(f"lambda:{function['FunctionName']}")
            
            # Check if Lambda function has S3 trigger
            try:
                s3_triggers = lambda_client.list_event_source_mappings(FunctionName=function['FunctionName'])
                for trigger in s3_triggers['EventSourceMappings']:
                    if trigger['EventSourceArn'].startswith('arn:aws:s3'):
                        bucket_name = trigger['EventSourceArn'].split(':')[-1]
                        connections.append((f"s3:{bucket_name}", f"lambda:{function['FunctionName']}"))
            except ClientError:
                pass
        
    except ClientError as e:
        click.echo(f"Error mining AWS data: {e}", err=True)
    
    return resources, connections

def generate_mermaid_diagram(resources: List[str], connections: List[Tuple[str, str]]) -> str:
    """Generate a Mermaid diagram from resources and connections."""
    diagram = "graph TD\n"
    for resource in resources:
        service, name = resource.split(':', 1)
        diagram += f"    {resource}[{service.upper()}: {name}]\n"
    for source, target in connections:
        diagram += f"    {source} --> {target}\n"
    return diagram

@click.command()
@click.option('--input-file', type=click.File('r'), help='Input Mermaid diagram file')
@click.option('--output-file', type=click.File('w'), required=True, help='Output Mermaid diagram file')
@click.option('--icons', default='aws_icons_mapping.json', help='AWS icons mapping file', type=click.Path(exists=True))
@click.option('--mine-aws', is_flag=True, help='Mine AWS data to generate diagram')
def main(input_file, output_file, icons, mine_aws):
    """Process a Mermaid diagram file and add AWS service icons, or generate a new diagram from AWS data."""
    icons_mapping = load_icons_mapping(icons)
    
    if mine_aws:
        click.echo("Mining AWS data...")
        resources, connections = mine_aws_data()
        input_diagram = generate_mermaid_diagram(resources, connections)
    elif input_file:
        click.echo(f"Processing {input_file.name}")
        input_diagram = input_file.read()
    else:
        click.echo("Error: Either --input-file or --mine-aws must be specified", err=True)
        return
    
    output_diagram = add_icons_to_mermaid(input_diagram, icons_mapping)
    
    output_file.write(output_diagram)
    click.echo(f"Processed diagram written to {output_file.name}")

if __name__ == "__main__":
    main()
