# Dockerfile
FROM ubuntu:22.04

# Temel bağımlılıkları yükle
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Ollama'yı yükle
RUN curl -fsSL https://ollama.com/install.sh | bash

# Ollama çalışma dizini
WORKDIR /root/.ollama

RUN ollama serve & \
    (while ! curl -s http://localhost:11434; do \
        sleep 2; \
    done) && \
    (ollama pull deepseek-r1:1.5b || exit 1) && \
    kill $(pgrep ollama)

# Portu aç
EXPOSE 11434

# Ollama servisini başlat
CMD ["ollama", "serve", "--address", "0.0.0.0:11434"]
