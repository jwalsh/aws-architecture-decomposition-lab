from typing import List, Tuple
import re
import os
import click
from pydantic import BaseModel, ValidationError

class MermaidNode(BaseModel):
    prefix: str
    service: str
    description: str

VALID_PREFIXES = [
    "amplify", "apigateway", "appflow", "appstream", "athena", "aurora", "backup", "batch",
    "cloudformation", "cloudfront", "cloudsearch", "cloudtrail", "cloudwatch", "codecommit",
    "codedeploy", "codepipeline", "cognito", "comprehend", "config", "connect", "databrew",
    "dms", "documentdb", "dynamodb", "ec2", "ecr", "ecs", "efs", "eks", "elasticache",
    "elasticbeanstalk", "elb", "emr", "eventbridge", "fargate", "fsx", "glacier", "glue",
    "guardduty", "iam", "inspector", "iot", "kinesis", "kms", "lambda", "lex", "macie", "msk",
    "neptune", "opensearch", "polly", "qldb", "quicksight", "rds", "redshift", "rekognition",
    "route53", "s3", "sagemaker", "secretsmanager", "securityhub", "ses", "sns", "sqs",
    "step_functions", "textract", "timestream", "transcribe", "translate", "vpc", "waf", "xray"
]

def parse_mermaid_node(line: str) -> Tuple[str, str, str]:
    match = re.search(r'(\w+):(\w+)\[([^]]+)\]', line)
    if match:
        prefix, service, description = match.groups()
        return prefix, service, description
    return "", "", ""

def audit_node(node: MermaidNode) -> Tuple[bool, bool]:
    valid_prefix = node.prefix.lower() in VALID_PREFIXES
    proper_specificity = node.prefix.lower() in node.service.lower()
    return valid_prefix, proper_specificity

def suggest_fix(node: MermaidNode, counter: int) -> str:
    fixed_prefix = node.prefix.lower()
    if fixed_prefix in VALID_PREFIXES:
        return f"{fixed_prefix}:{fixed_prefix}{counter}[{node.description}]"
    return ""

@click.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--output-dir', default='diagrams-fixed', type=click.Path(), help='Directory to save fixed diagrams.')
def audit_and_fix_mermaid_diagrams(directory: str, output_dir: str):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.mmd'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    lines = f.readlines()

                fixed_lines = []
                node_counter = {}
                
                for line in lines:
                    prefix, service, description = parse_mermaid_node(line)
                    if prefix and service:
                        try:
                            node = MermaidNode(prefix=prefix, service=service, description=description)
                            valid_prefix, proper_specificity = audit_node(node)
                            if not valid_prefix or not proper_specificity:
                                new_prefix = prefix.lower()
                                if new_prefix not in node_counter:
                                    node_counter[new_prefix] = 1
                                else:
                                    node_counter[new_prefix] += 1
                                fixed_node = suggest_fix(node, node_counter[new_prefix])
                                fixed_lines.append(line.replace(f"{prefix}:{service}[{description}]", fixed_node))
                            else:
                                fixed_lines.append(line)
                        except ValidationError as e:
                            click.echo(f"Validation error in file {file}: {e}")
                            fixed_lines.append(line)
                    else:
                        fixed_lines.append(line)

                # Write the fixed diagram to the output directory
                fixed_filepath = os.path.join(output_dir, file)
                with open(fixed_filepath, 'w') as f:
                    f.writelines(fixed_lines)

                click.echo(f"Fixed diagram saved to {fixed_filepath}")

if __name__ == '__main__':
    audit_and_fix_mermaid_diagrams()
