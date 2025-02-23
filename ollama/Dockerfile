FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y curl build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://ollama.com/install.sh | bash

WORKDIR /ollama

RUN ollama serve & \
    (while ! curl -s http://localhost:11434; do \
        sleep 2; \
    done) && \
    (ollama pull qwen2.5:1.5b || exit 1) && \
    kill $(pgrep ollama)

EXPOSE 11434

CMD ["ollama", "serve"]
