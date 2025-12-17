# Base image: ubuntu:22.04
FROM ubuntu:22.04

# ARGs
# https://docs.docker.com/engine/reference/builder/#understand-how-arg-and-from-interact
ARG TARGETPLATFORM=linux/amd64,linux/arm64
ARG DEBIAN_FRONTEND=noninteractive

# neo4j 2025.08.0 installation (match GDS v2.21.0) and some cleanup
RUN apt-get update && \
    apt-get install -y wget gnupg software-properties-common && \
    wget -O - https://debian.neo4j.com/neotechnology.gpg.key | apt-key add - && \
    echo 'deb https://debian.neo4j.com stable latest' > /etc/apt/sources.list.d/neo4j.list && \
    add-apt-repository universe && \
    apt-get update && \
    apt-get install -y nano unzip neo4j=1:2025.08.0 python3-pip && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


#********************************************** MY CODE *************************************************************************

# Workdir
RUN mkdir -p /cse511
WORKDIR /cse511

# Java 21
RUN apt-get update && apt-get install -y openjdk-21-jdk && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64

# Python deps
RUN python3 -m pip install --upgrade pip && pip install neo4j pandas pyarrow

# Dataset
ADD https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2022-03.parquet /cse511/yellow_tripdata_2022-03.parquet

# Loader
COPY ./data_loader.py /cse511/data_loader.py

# GDS plugin
RUN mkdir -p /var/lib/neo4j/plugins && \
    wget -O /var/lib/neo4j/plugins/neo4j-graph-data-science-2.21.0.jar \
    https://github.com/neo4j/graph-data-science/releases/download/2.21.0/neo4j-graph-data-science-2.21.0.jar


# Neo4j config (v5 server.* keys) + APOC in apoc.conf
RUN echo "server.default_listen_address=0.0.0.0" >> /etc/neo4j/neo4j.conf && \
    echo "server.bolt.listen_address=:7687"       >> /etc/neo4j/neo4j.conf && \
    echo "server.http.listen_address=:7474"       >> /etc/neo4j/neo4j.conf && \
    echo "dbms.security.procedures.unrestricted=gds.*,apoc.*" >> /etc/neo4j/neo4j.conf && \
    echo "dbms.security.procedures.allowlist=gds.*,apoc.*"    >> /etc/neo4j/neo4j.conf && \
    echo "apoc.import.file.enabled=true" >> /etc/neo4j/apoc.conf && \
    mkdir -p /var/lib/neo4j/import && \
    chown -R neo4j:neo4j /var/lib/neo4j /etc/neo4j /var/log/neo4j

# --- Initialize password & fix permissions for Neo4j ---
RUN mkdir -p /var/log/neo4j && \
    touch /var/log/neo4j/{neo4j.log,debug.log,http.log,query.log,security.log} && \
    chown -R neo4j:neo4j /var/lib/neo4j /var/log/neo4j /etc/neo4j && \
    runuser -u neo4j -- neo4j-admin dbms set-initial-password graphprocessing


# Ensure runtime auth is applied (no manual steps at grading)
ENV NEO4J_AUTH=neo4j/graphprocessing

#******************************************************************************************************************


# Run the data loader script
RUN chmod +x /cse511/data_loader.py && \
    neo4j start && \
    python3 data_loader.py && \
    neo4j stop

# Expose neo4j ports
EXPOSE 7474 7687

# Start neo4j service and show the logs on container run
CMD ["/bin/bash", "-c", "neo4j start && tail -f /dev/null"]
