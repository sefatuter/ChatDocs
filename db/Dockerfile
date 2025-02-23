FROM postgres:17

RUN apt-get update && apt install postgresql-17-pgvector && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
    
COPY ..db/init.sql /docker-entrypoint-initdb.d/init.sql

ENV POSTGRES_DB=pgllm
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=psql1234
ENV PG_HOST=localhost
ENV PG_PORT = 5432

