#!/bin/sh

# Start Ollama in the background
/bin/ollama serve &
pid=$!

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
# Use a simple loop to check if the port is open
while ! nc -z localhost 11434; do
  sleep 2
done

echo "🔴 Pulling nomic-embed-text..."
ollama pull nomic-embed-text
echo "🔴 Pulling gemma4:e4b..."
ollama pull gemma4:e4b
echo "🟢 Models ready!"

# Wait for the Ollama process
wait $pid