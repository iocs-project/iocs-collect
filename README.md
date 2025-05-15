# iocs-collect

# Threat Feed Collector

This is the **core component** responsible for downloading and storing malicious IP and URL addresses into a PostgreSQL database. It relies on an own library [`db-utils`](https://github.com/iocs-project/db-utils) for database connection management and requires all SQL scripts to be applied before runtime, handled by the companion project [`db-postgre-sql`](https://github.com/iocs-project/db-postgre-sql).

The application supports both **data ingestion** from external sources and **searching** for known threats in the database.

---

## 📚 Overview

- Downloads malicious IP and URL feeds.
- Stores the data in a PostgreSQL database.
- Provides functionality to search for known threats.
- Depends on a PostgreSQL deployment managed via `db-postgre-sql`.

---

## 🔧 Requirements

- Python 3.12+
- PostgreSQL 15+
- Docker Compose

---

## 🚀 Setup

The easiest way to start the entire system is by running:

```bash
./run.sh
```
---
  

## 🚀 Architecture

```
                      +----------------+
                      |   db-utils     |
                      | (shared lib)   |
                      +--------+-------+
                               |
           +-------------------+-------------------+
           |                                       |
+-----------------------+           +-----------------------------+
|    db-postgre-sql     |           |        iocs-collect         |
|-----------------------|           |-----------------------------|
| - Contains SQL scripts|           | - Downloads threat feeds    |
| - Applies schema to   |           | - Searches IPs and URLs     |
|   PostgreSQL DB       |           | - Requires DB to be ready   |
|                       |           | - Uses db-utils for DB conn |
+-----------+-----------+           +-------------+---------------+
            |                                       |
            |                                       |
            |              Depends on               |
            |-------------------------------------->|
                          PostgreSQL DB
```

## 🚀 ER diagram

![Untitled](https://github.com/user-attachments/assets/4c32ae69-4aa8-4c2e-922b-093b9b4bb61b)
