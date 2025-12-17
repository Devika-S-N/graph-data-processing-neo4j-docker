# Graph Data Processing with Neo4j & Docker

## Overview
This project demonstrates graph-based data processing at scale using **Neo4j**, fully containerized with **Docker**.  
A real-world transportation dataset (NYC Taxi Trips) is modeled as a graph and analyzed using classic graph algorithms.

The goal of this project was to build a **reproducible graph database system**, load large-scale data programmatically, and apply graph analytics such as **PageRank** and **Breadth First Search (BFS)**.

---

## Project Objectives
- Build a Dockerized Neo4j environment with zero manual setup
- Load a real-world dataset into a graph database
- Model transportation data using nodes and relationships
- Implement and run graph algorithms using Neo4j GDS

---

## What Was Achieved
- Automated Neo4j setup using Docker
- Programmatic loading of NYC Taxi trip data
- Graph modeling of pickup and drop-off locations
- PageRank implementation to rank important locations
- BFS implementation to find paths between locations
- Clean, reproducible, and scalable system design

---

## Graph Model

### Nodes
- **Label:** `Location`
- **Property:**
  - `name` (location ID)

### Relationships
- **Type:** `TRIP`
- **Properties:**
  - `distance` (float)
  - `fare` (float)
  - `pickup_dt` (datetime)
  - `dropoff_dt` (datetime)

This model enables efficient traversal and analytics on transportation data.

---

## Technologies Used
- **Docker** – containerized deployment
- **Neo4j** – graph database
- **Neo4j Graph Data Science (GDS)** – PageRank and BFS
- **Python** – data loading and graph querying
- **Cypher** – graph query language

---

## Project Structure
```bash
graph-data-processing-neo4j-docker/
├── Dockerfile          # Builds Neo4j + GDS environment
├── data_loader.py      # Loads NYC Taxi data into Neo4j
├── interface.py        # Implements PageRank and BFS
├── README.md
└── .gitignore
```

---

## How to Run

### Build the Docker Image
```bash
docker build -t graph-project .
```
### Run the Container
```bash
docker build -t graph-project .

