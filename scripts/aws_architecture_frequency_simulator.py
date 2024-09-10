#!/usr/bin/env python3
"""
AWS Architecture Frequency Simulator (AAFS)

This script analyzes Mermaid diagrams representing AWS architectures,
tracks service usage frequency in a SQLite database, and simulates
new architectures based on historical weights using a Markov chain.
"""

import re
import json
import sqlite3
from typing import Dict, List, Tuple
import click
import itertools
from functools import reduce
from collections import Counter
import random

# Inline data file for AWS service mappings
AWS_SERVICES = {
    "ec2": "Amazon EC2",
    "s3": "Amazon S3",
    "lambda": "AWS Lambda",
    "dynamodb": "Amazon DynamoDB",
    "rds": "Amazon RDS",
    "cloudfront": "Amazon CloudFront",
    "apigateway": "Amazon API Gateway",
    "sns": "Amazon SNS",
    "sqs": "Amazon SQS",
    "kinesis": "Amazon Kinesis",
    # Add more services as needed
}

def init_db() -> sqlite3.Connection:
    """Initialize SQLite database for storing service frequencies."""
    conn = sqlite3.connect('aws_service_frequency.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS service_frequency
                 (service TEXT PRIMARY KEY, frequency INTEGER)''')
    conn.commit()
    return conn

def parse_mermaid(mermaid_diagram: str) -> List[str]:
    """
    Parse a Mermaid diagram and extract AWS service names.

    Args:
        mermaid_diagram (str): The Mermaid diagram as a string.

    Returns:
        List[str]: A list of AWS service names found in the diagram.
    """
    service_pattern = r'(\w+):'
    return re.findall(service_pattern, mermaid_diagram)

def update_frequency_db(conn: sqlite3.Connection, services: List[str]):
    """
    Update the frequency count of AWS services in the database.

    Args:
        conn (sqlite3.Connection): Database connection.
        services (List[str]): List of AWS service names.
    """
    c = conn.cursor()
    for service in services:
        if service in AWS_SERVICES:
            c.execute('''INSERT INTO service_frequency (service, frequency)
                         VALUES (?, 1)
                         ON CONFLICT(service) DO UPDATE SET
                         frequency = frequency + 1''', (service,))
    conn.commit()

def process_itertools(services: List[str]) -> Dict[str, int]:
    """
    Process services using itertools.

    Args:
        services (List[str]): List of AWS service names.

    Returns:
        Dict[str, int]: Frequency count of services.
    """
    return dict(Counter(filter(lambda s: s in AWS_SERVICES, services)))

def process_map_reduce(services: List[str]) -> Dict[str, int]:
    """
    Process services using map-reduce.

    Args:
        services (List[str]): List of AWS service names.

    Returns:
        Dict[str, int]: Frequency count of services.
    """
    mapped = map(lambda s: (s, 1) if s in AWS_SERVICES else None, services)
    filtered = filter(None, mapped)
    return dict(reduce(lambda x, y: {**x, y[0]: x.get(y[0], 0) + y[1]}, filtered, {}))

def process_pure_python(services: List[str]) -> Dict[str, int]:
    """
    Process services using pure Python.

    Args:
        services (List[str]): List of AWS service names.

    Returns:
        Dict[str, int]: Frequency count of services.
    """
    frequency = {}
    for service in services:
        if service in AWS_SERVICES:
            frequency[service] = frequency.get(service, 0) + 1
    return frequency

def get_historical_weights(conn: sqlite3.Connection) -> Dict[str, int]:
    """
    Get historical weights from the database.

    Args:
        conn (sqlite3.Connection): Database connection.

    Returns:
        Dict[str, int]: Historical weights of services.
    """
    c = conn.cursor()
    c.execute("SELECT service, frequency FROM service_frequency")
    return dict(c.fetchall())

def create_markov_chain(weights: Dict[str, int]) -> Dict[str, List[Tuple[str, float]]]:
    """
    Create a Markov chain from historical weights.

    Args:
        weights (Dict[str, int]): Historical weights of services.

    Returns:
        Dict[str, List[Tuple[str, float]]]: Markov chain representation.
    """
    total = sum(weights.values())
    chain = {}
    for service, count in weights.items():
        transitions = [(next_service, next_count / total) for next_service, next_count in weights.items()]
        chain[service] = transitions
    return chain

def generate_architecture(chain: Dict[str, List[Tuple[str, float]]], start_service: str, length: int) -> List[str]:
    """
    Generate a new architecture using the Markov chain.

    Args:
        chain (Dict[str, List[Tuple[str, float]]]): Markov chain.
        start_service (str): Starting service.
        length (int): Desired length of the architecture.

    Returns:
        List[str]: Generated architecture.
    """
    architecture = [start_service]
    for _ in range(length - 1):
        transitions = chain[architecture[-1]]
        next_service = random.choices([t[0] for t in transitions], weights=[t[1] for t in transitions])[0]
        architecture.append(next_service)
    return architecture

@click.command()
@click.argument('input_file', type=click.File('r'))
@click.option('--method', type=click.Choice(['itertools', 'map_reduce', 'pure_python']), default='pure_python', help='Processing method')
@click.option('--simulate', is_flag=True, help='Simulate new architecture')
@click.option('--length', default=5, help='Length of simulated architecture')
def main(input_file: click.File, method: str, simulate: bool, length: int):
    """
    Analyze AWS architecture diagram, update service frequency, and optionally simulate new architecture.

    Args:
        input_file (click.File): Input file containing the Mermaid diagram.
        method (str): Processing method to use.
        simulate (bool): Flag to simulate new architecture.
        length (int): Length of simulated architecture.
    """
    conn = init_db()
    mermaid_diagram = input_file.read()
    services = parse_mermaid(mermaid_diagram)

    if method == 'itertools':
        frequency = process_itertools(services)
    elif method == 'map_reduce':
        frequency = process_map_reduce(services)
    else:
        frequency = process_pure_python(services)

    update_frequency_db(conn, services)
    click.echo("Updated frequency in database:")
    click.echo(json.dumps(frequency, indent=2))

    if simulate:
        weights = get_historical_weights(conn)
        chain = create_markov_chain(weights)
        start_service = random.choice(list(weights.keys()))
        new_architecture = generate_architecture(chain, start_service, length)
        click.echo("\nSimulated Architecture:")
        click.echo(" -> ".join(new_architecture))

    conn.close()

if __name__ == "__main__":
    main()
