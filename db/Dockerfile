FROM postgres:16.7

# Install dependencies
RUN apt-get update && apt-get install -y \
    postgresql-server-dev-16 \
    postgresql-common \
    gcc \
    make \
    git

# Download and install pgvector
RUN cd /tmp && \
    git clone --branch v0.5.0 https://github.com/pgvector/pgvector.git && \
    cd pgvector && \
    make && \
    make install && \
    rm -rf /tmp/pgvector  # Clean up to reduce image size

# Ensure pgvector is enabled on database creation
RUN echo "CREATE EXTENSION IF NOT EXISTS vector;" >> /docker-entrypoint-initdb.d/init.sql

ENV POSTGRES_DB=pgllm
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=psql1234
ENV PG_HOST=localhost
ENV PG_PORT = 5432

