#!/bin/bash

# initialize_db.sh

# Check if the database file already exists
if [ -f aws_architecture_responses.db ]; then
    echo "Database file already exists. Do you want to overwrite it? (y/n)"
    read answer
    if [ "$answer" != "${answer#[Yy]}" ]; then
        rm aws_architecture_responses.db
        echo "Existing database removed."
    else
        echo "Exiting without changes."
        exit 0
    fi
fi

# Run the seed script
sqlite3 aws_architecture_responses.db < seed_aws_architecture_db.sql

echo "Database initialized successfully."
