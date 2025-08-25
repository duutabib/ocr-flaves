#!/bin/sh
set -e

# Start Ollama in the background
ollama serve &

# Wait for Ollama to be ready
until curl -s http://localhost:11434 > /dev/null; do
    echo "Waiting for Ollama to start..."
    sleep 1
done

# Pull the model if it doesn't exist
if ! ollama list | grep -q "llava"; then
    echo "Pulling LLaVA model..."
    ollama pull llava
fi

# Keep the container running
wait