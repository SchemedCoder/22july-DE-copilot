# 🗄️ DE Copilot – AI-Powered Data Engineering Assistant

An AI-powered Data Engineering Copilot that answers questions about ETL/ELT pipelines, schema handling, deduplication, SQL transformations, and data engineering best practices using Retrieval-Augmented Generation (RAG).

The application indexes project documentation, SQL files, Python scripts, and JSON schemas into a Qdrant vector database and uses Groq LLM to answer user queries with source citations.

---

# Features

- AI-powered Data Engineering Assistant
- Retrieval-Augmented Generation (RAG)
- Semantic search using Qdrant
- Fast responses using Groq LLM
- Streamlit UI
- Source-aware answers
- Snowflake integration demo
- Supports Python, SQL, Markdown and JSON documentation

---

# Tech Stack

- Python
- Streamlit
- Qdrant Vector Database
- Groq LLM
- FastEmbed
- Snowflake Connector
- SQLAlchemy
- Pandas
- dotenv

---

# Project Structure

```
de-copilot/
│
├── app.py                     # Streamlit application
├── ingest.py                  # Builds vector database
├── requirements.txt
├── .env
│
├── data_sources/
│   ├── docs/
│   │     schema_similarisation.md
│   │
│   ├── python/
│   │     data_framing.py
│   │
│   ├── sql/
│   │     deduplication_dbt.sql
│   │
│   └── schemas/
│         user_events.json
│
├── demo/
│      run_snowflake.py
│
└── qdrant_db/
```

---

# Architecture

```
Project Files
(SQL + Python + Markdown + JSON)
              │
              ▼
         ingest.py
              │
              ▼
      FastEmbed Embeddings
              │
              ▼
        Qdrant Vector DB
              │
              ▼
         User Question
              │
              ▼
      Semantic Retrieval
              │
              ▼
          Groq LLM
              │
              ▼
     Source-backed Answer
```

---

# Setup

## Clone

```bash
git clone https://github.com/SchemedCoder/22july-DE-copilot.git
cd 22july-DE-copilot
```

---

## Create Virtual Environment

```bash
python -m venv .venv
```

Windows

```bash
.venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Create .env

```text
GROQ_API_KEY=your_api_key

SNOWFLAKE_ACCOUNT=xxxx
SNOWFLAKE_USER=xxxx
SNOWFLAKE_PASSWORD=xxxx
SNOWFLAKE_DATABASE=xxxx
SNOWFLAKE_SCHEMA=xxxx
SNOWFLAKE_WAREHOUSE=xxxx
SNOWFLAKE_ROLE=xxxx
```

---

# Build Vector Database

```bash
python ingest.py
```

Expected output

```
Starting data ingestion...
Adding 4 documents to Qdrant...
Ingestion complete!
```

---

# Run the Application

```bash
streamlit run app.py
```

---

# Supported Questions

Examples:

- Explain schema handling
- How do we perform deduplication?
- What is the difference between ETL and ELT?
- Explain timestamp handling
- Explain data framing
- Explain dbt transformations
- Explain Snowflake loading
- Explain schema normalization
- Explain event aggregation

---

# How Schema Handling Works

The project performs schema standardization before loading data.

### Column Mapping

Different source names are mapped into a common schema.

Example

```
cust_id
↓

user_id
```

---

### Data Type Conversion

String timestamps are converted into datetime.

```python
events_df["event_timestamp"] = pd.to_datetime(
    events_df["event_timestamp"]
)
```

---

### Value Normalization

Example

```
M → Male

F → Female
```

This ensures consistent analytics across multiple data sources.

---

# Timestamp Handling

Timestamp fields are converted into datetime.

The pipeline then extracts

- Event Date
- First Event Time
- Last Event Time

Example

```python
events_df["event_date"] = events_df["event_timestamp"].dt.date
```

Used for

- Daily aggregation
- Event ordering
- Time-based reporting

---

# Deduplication Strategy

Deduplication is implemented using SQL (dbt).

Business logic:

- Partition records by User ID
- Order by Updated Timestamp
- Keep the latest record
- Remove older duplicates

Typical implementation

```sql
ROW_NUMBER() OVER (
PARTITION BY user_id
ORDER BY updated_at DESC
)
```

Only rows with

```
ROW_NUMBER = 1
```

are retained.

This ensures a single latest record per user.

---

# ETL or ELT?

This project primarily follows an **ELT** architecture.

### Extract

Read raw JSON, SQL and documentation.

↓

### Load

Load data into the warehouse.

↓

### Transform

Perform transformations using SQL/dbt.

Advantages

- Warehouse performs transformations
- Better scalability
- Faster analytics
- Easier maintenance

Python is mainly used for preprocessing and vector ingestion.

---

# RBAC

Current project status

RBAC is **not implemented**.

For production systems, RBAC would typically be implemented using Snowflake roles.

Example

```
ADMIN

↓

DATA_ENGINEER

↓

ANALYST

↓

READ_ONLY
```

Permissions

- SELECT
- INSERT
- UPDATE
- CREATE
- OWNERSHIP

This follows the Principle of Least Privilege.

---

# Snowflake Demo

The project also demonstrates loading processed data into Snowflake tables using

- Snowflake Connector
- SQLAlchemy

Example target tables

- CLEAN_USERS
- DAILY_EVENTS_DATAMART

---
