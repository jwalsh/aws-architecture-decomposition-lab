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

def suggest_fix(node: MermaidNode) -> str:
    if not node.prefix:
        suggested_prefix = next((prefix for prefix in VALID_PREFIXES if prefix in node.description.lower()), None)
        if suggested_prefix:
            return f"{suggested_prefix}:{node.service.lower()}[{node.description}]"
    elif node.prefix.lower() not in VALID_PREFIXES:
        suggested_prefix = next((prefix for prefix in VALID_PREFIXES if prefix in node.description.lower()), None)
        if suggested_prefix:
            return f"{suggested_prefix}:{node.service.lower()}[{node.description}]"
    return ""

@click.command()
@click.argument('directory', type=click.Path(exists=True))
def audit_mermaid_diagrams(directory: str):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.mmd'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    lines = f.readlines()

                warnings = 0
                failures = 0
                fixes = []
                for line in lines:
                    prefix, service, description = parse_mermaid_node(line)
                    if prefix and service:
                        try:
                            node = MermaidNode(prefix=prefix, service=service, description=description)
                            valid_prefix, proper_specificity = audit_node(node)
                            if not valid_prefix:
                                click.echo(f"Warning: Invalid prefix '{node.prefix}' in file {file}")
                                warnings += 1
                                fix = suggest_fix(node)
                                if fix:
                                    fixes.append(f"Suggested fix: {fix}")
                            if not proper_specificity:
                                click.echo(f"Failure: Service '{node.service}' lacks intended specificity in file {file}")
                                failures += 1
                                fix = suggest_fix(node)
                                if fix:
                                    fixes.append(f"Suggested fix: {fix}")
                        except ValidationError as e:
                            click.echo(f"Validation error in file {file}: {e}")

                if warnings == 0 and failures == 0:
                    click.echo(f"All nodes in {file} are valid and properly specific.")
                else:
                    click.echo(f"{warnings} warning(s) and {failures} failure(s) found in {file}.")
                    for fix in fixes:
                        click.echo(fix)

if __name__ == '__main__':
    audit_mermaid_diagrams()
