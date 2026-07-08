# E-Commerce Order Analytics System 🚀

An end-to-end data analytics engineering pipeline built using **Python** and **SQL (SQLite)**. This system automates the lifecycle of e-commerce transactional data—from raw, messy synthetic data generation to automated cleaning, relational warehousing, complex analytical reporting, and validation testing through an interactive Command Line Interface (CLI).

---

## 🏗️ System Architecture & Workflow

The architecture strictly maintains a modular separation of concerns across multiple layered stages:

1. **Data Generation Layer (`generate_data.py`)**: Uses synthetic rules to simulate production databases across 4 core vectors (`customers`, `products`, `orders`, `order_items`), intentionally embedding real-world anomalies (null references, timestamp inconsistencies, invalid emails, negative bounds).
2. **Data Cleaning & Engine Ingestion Layer (`clean_data.py`)**: Harnesses Pandas to apply regex validation, boolean masks for referential boundaries, title casing, and timestamp parsing. Once structured, it auto-instantiates `schema.sql` to build the physical analytical relational warehouse.
3. **Analytics Logic Matrix (`sql/`)**: Segmented SQL matrices running basic aggregates, advanced Window functions (`DENSE_RANK()`, `LAG()`, `NTILE()`), multi-tiered CTEs, and rigorous calculation models for Monthly Cohort Retention curves.
4. **Interactive CLI Presentation Engine (`report_cli.py`)**: A pure Python CLI framework utilizing no external layout dependencies. It enforces strict exception handling for connection boundaries, date filters, and displays outputs in dynamic grid tables.

---

## 📁 Repository Directory Structure

```text
ecommerce-analytics-system/
│── data/
│   ├── raw/
│   │   ├── customers.csv
│   │   ├── products.csv
│   │   ├── orders.csv
│   │   └── order_items.csv
│   └── cleaned/
│       ├── customers_clean.csv
│       ├── products_clean.csv
│       ├── orders_clean.csv
│       └── order_items_clean.csv
│   └── ecommerce_warehouse.db       <- Consolidated SQLite Production Database
│── scripts/
│   ├── generate_data.py             <- Phase 1: Data Generation Engine
│   ├── clean_data.py                <- Phase 2 & 3: ETL Pipeline & Warehouse Ingestion
│   └── report_cli.py                <- Phase 4 & 5: Presentation CLI Tool & Audits
│── sql/
│   ├── schema.sql                   <- DDL Structures with explicit PK/FK/Constraints
│   ├── aggregations.sql             <- Queries 1-6: Basic & Intermediate Analytics
│   ├── window_functions.sql         <- Queries 7-14: Windowing, Ranking, and YoY Matrices
│   └── cohort_analysis.sql          <- Queries 15-16: Complex Retention Cohorts
│── output/
│   └── sample_reports/              <- Saved Execution Log Screens
│── README.md                        <- Documentation Architecture Blueprint