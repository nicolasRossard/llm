#!/bin/bash

# Start Ollama in the background.
/bin/ollama serve &
# Record Process ID.
pid=$!

# Pause for Ollama to start.
sleep 5

echo "Retrieving model (llama3.1)..."
ollama pull llama3.2:1b
echo "Retrieving model (llama3.1)..."
ollama pull nomic-embed-text:v1.5
echo "Done."

# Wait for Ollama process to finish.
wait $pid