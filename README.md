# Pharmaceutical Procurement Intelligence: Multi-File JSON-to-CSV Flattener & Deduplicator

## Project Overview

This repository contains a pure Python batch ingestion pipeline for consolidating pharmaceutical procurement supplier quotes received through multiple nested JSON batch files.

The solution dynamically discovers incoming JSON files, extracts and flattens nested supplier, material, and pricing attributes, handles optional missing fields using defensive dictionary access, and eliminates cross-file duplicate quote records using Python's in-memory set data structure.
The pipeline also calculates derived financial metrics, including gross order value and net order value, generates UTC processing timestamps, exports the consolidated records into a structured CSV report, and maintains operational logs for execution monitoring.

The entire solution is implemented using Python Standard Library modules only, without relying on third-party data processing libraries or database systems.

## Repository Structure

```text
pharma-quote-consolidator/
│
├── data/
│   ├── quotes_incoming/
│   │   ├── quote_batch_1.json
│   │   ├── quote_batch_2.json
│   │   └── quote_batch_3.json
│   │
│   └── output/
│       # Consolidated CSV output (Ignored by Git)
│
├── logs/
│   # Execution logs (Ignored by Git)
│
├── src/
│   └── consolidate_quotes.py
│       # Primary Python ETL engine
│
├── .gitignore
│   # Git exclusion rules
│
└── README.md
    # Project documentation and execution instructions
```

## Technologies & Libraries

The project strictly uses Python Standard Library modules:

- `pathlib` – Dynamic file discovery and directory management.
- `json` – Reading and parsing nested JSON batch files.
- `csv` – Exporting flattened records using `csv.DictWriter`.
- `datetime` – Generating UTC processing timestamps.
- `logging` – Operational logging and execution monitoring.

**Prohibited Libraries and Tools:**

- pandas
- polars
- numpy
- SQL databases
- Third-party Python packages

## Setup & Installation

### 1. Clone the repository locally

```bash
git clone https://github.com/<your-username>/pharma-quote-consolidator.git

cd pharma-quote-consolidator
```

### 2. Verify Python installation

Ensure Python is installed on your system.

```bash
python --version
```

No third-party package installation or `requirements.txt` file is required because the project uses only Python Standard Library modules.

### 3. Verify the input files

Ensure the following JSON batch files are available inside `data/quotes_incoming/`:

```text
quote_batch_1.json
quote_batch_2.json
quote_batch_3.json
```

## Pipeline Execution

Run the complete JSON-to-CSV ingestion pipeline from the project root directory:

```bash
python src/consolidate_quotes.py
```

The pipeline performs the following operations:

1. Dynamically discovers incoming JSON batch files.
2. Reads and parses nested JSON records.
3. Extracts and flattens supplier, material, and pricing attributes.
4. Inherits batch-level metadata into individual quote records.
5. Handles missing optional fields using default values.
6. Identifies and skips duplicate quote IDs across files.
7. Calculates gross and net order values.
8. Generates UTC processing timestamps.
9. Exports consolidated records into a CSV file.
10. Generates structured operational logs and execution metrics.

## Verification & Output Rules

Upon successful execution, the pipeline generates the following outputs:

**1. Consolidated CSV Report**

Location: `data/output/consolidated_quotes.csv`

Contains the flattened and deduplicated pharmaceutical procurement quote records, including supplier information, material details, pricing attributes, calculated financial metrics, validity dates, and processing timestamps.

**2. Execution Log**

Location: `logs/pipeline.log`

Contains structured execution logs, duplicate warnings, processing information, and final execution summary metrics.

## Expected Execution Summary

Based on the three supplied sample JSON batch files, the expected processing results are:

| Metric | Expected Value |
|---|---:|
| Files scanned | 3 |
| Total quotes read | 8 |
| Duplicates skipped | 2 |
| Unique quotes written | 6 |

**Duplicate Quote IDs:**

- `QT-5002` – Duplicate found in `quote_batch_2.json`.
- `QT-5001` – Duplicate found in `quote_batch_3.json`.

The final consolidated CSV must contain exactly **6 unique quote records**, preserving the alphabetical file ingestion order.

## Version Control & Data Management

The `.gitignore` file excludes generated output files, execution logs, Python cache files, and virtual environments from Git version control.

The original JSON input files, source code, project documentation, and required project structure are maintained in the GitHub repository.

---

**Project Domain:** Pharmaceutical Procurement & Supply Chain Intelligence

**Project Type:** Pure Python Batch Data Ingestion and Transformation

**Implementation:** Python Standard Library Only
