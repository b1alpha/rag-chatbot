#!/bin/bash

# Check if a question was provided
if [ -z "$1" ]; then
    echo "Usage: ./ask.sh 'Your question here'"
    exit 1
fi

# URL encode the question
QUESTION=$(echo "$1" | jq -R -s -r @uri)

# Make the request
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"$1\"}" | jq .
