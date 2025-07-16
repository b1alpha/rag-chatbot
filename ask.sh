#!/bin/bash

# Check if a question was provided
if [ -z "$1" ]; then
    echo "Usage: ./ask.sh 'Your question here'"
    exit 1
fi

# URL encode the question
QUESTION=$(echo "$1" | jq -R -s -r @uri)

# # Make the request
# curl -X POST http://localhost:8000/query \
#   -H "Content-Type: application/json" \
#   -d "{\"question\": \"$1\"}" | jq .

# save the response and pipe it into a futher pretty print
RESPONSE=$(curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"$1\"}")

echo "$RESPONSE" | jq .
# futher pretty print
echo "$RESPONSE" | jq -r '.answer' | sed 's/\\n/\n/g' | sed 's/\\t/\t/g'  | sed 's/\\r/\r/g' | sed 's/\\f/\f/g' | sed 's/\\v/\v/g'
