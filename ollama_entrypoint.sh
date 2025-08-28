#!/bin/bash

# Start Ollama in the background.
/bin/ollama serve &
# Record Process ID.
pid=$!

# Pause for Ollama to start.
sleep 5

echo "Retrieving model (llama3.1)..."
ollama pull llama3.2:1b

echo "Retrieving model (nomic-embed-text:v1.5)..."
ollama pull nomic-embed-text:v1.5
echo "Done."

echo "Retrieving model (gemma3:270m)..."
ollama pull gemma3:270m
echo "Done."

# Vision for documents ibm/granite3.3-vision:2b
# Wait for Ollama process to finish.
wait $pid