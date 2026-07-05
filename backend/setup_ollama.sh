#!/bin/sh
# Start Ollama in the background
/bin/ollama serve &
# Record the process ID
pid=$!
# Wait for Ollama to start up
sleep 5
echo "🔴 Pulling nomic-embed-text..."
ollama pull nomic-embed-text
echo "🔴 Pulling gemma4:e4b..."
ollama pull gemma4:e4b
echo "🟢 Models ready!"
# Wait for the Ollama process to keep running
wait $pid