
#########################################################################################
"""
Script Name    : consolidate_quotes.py
Objective      : Discover multiple JSON batch files, flatten nested pharmaceutical
                 supplier quote records and eliminate cross-file duplicates.
Created By     : TEAM 1 (Jai Shivani, Jai Balaji, Aayushi)
Created Date   : 26-11-2026
Modified By    : TEAM 1
Modified Date  : 26-11-2026

#########################################################################################

PSEUDOCODE:

Step 1: Import required libraries, define project directories and initialize logging.

Step 2: Discover JSON files and read using JSON parsing.

Step 3: Extract batch-level metadata and flatten nested JSON records.

Step 4: Identify and eliminate duplicate across files using an in-memory set while retaining unique quote records.

Step 5: Log processed file and display the execution summary.

END
"""
#########################################################################################


# ============================================================
# IMPORT REQUIRED LIBRARIES
# ============================================================

import json
import logging
import sys

from pathlib import Path
from datetime import datetime


# ============================================================
# STEP 1: DEFINE PROJECT DIRECTORIES AND INITIALIZE LOGGING
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_DIR = BASE_DIR / "data" / "quotes_incoming"
OUTPUT_DIR = BASE_DIR / "data" / "output"
LOG_DIR = BASE_DIR / "logs"

# Create required directories

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Generate a unique timestamp for each execution

RUN_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

# Define log file paths

LOG_FILE = LOG_DIR / "consolidate_quotes.log"
RUN_LOG_FILE = LOG_DIR / f"consolidate_quotes_{RUN_TIMESTAMP}.log"


def initialize_logging():

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),

            # Shared log file
            logging.FileHandler(
                LOG_FILE,
                mode="a",
                encoding="utf-8"
            ),

            # Separate timestamped log file for each execution
            logging.FileHandler(
                RUN_LOG_FILE,
                mode="w",
                encoding="utf-8"
            )
        ],
        force=True
    )

    # First log entry

    logging.info(
        "%s started at %s",
        Path(__file__).name,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    logging.info(
        "STEP 1 STARTED: Initialize project directories and logging"
    )

    logging.info("Input directory: %s", INPUT_DIR)
    logging.info("Output directory: %s", OUTPUT_DIR)
    logging.info("Shared log file: %s", LOG_FILE)
    logging.info("Run-specific log file: %s", RUN_LOG_FILE)

    logging.info(
        "STEP 1 COMPLETED: Logging initialized successfully"
    )


# ============================================================
# STEP 2: DYNAMICALLY DISCOVER AND READ JSON FILES
# ============================================================

def discover_json_files():

    logging.info("STEP 2 STARTED: Discover incoming JSON files")

    json_files = sorted(INPUT_DIR.glob("*.json"))

    logging.info("JSON files discovered: %d", len(json_files))

    for file_path in json_files:
        logging.info("Discovered file: %s", file_path.name)

    logging.info("STEP 2 COMPLETED: JSON file discovery")

    return json_files


def read_json_files(json_files):

    logging.info("Reading discovered JSON batch files")

    raw_quotes = []

    total_quotes_read = 0
    files_processed = 0
    failed_files = 0

    for file_path in json_files:

        logging.info("Reading file: %s", file_path.name)

        try:

            with open(file_path, "r", encoding="utf-8") as file:
                batch_data = json.load(file)

            if not isinstance(batch_data, dict):
                raise ValueError("JSON root must be an object")

            quotes = batch_data.get("quotes", [])

            if not isinstance(quotes, list):
                raise ValueError("Quotes field must contain a list")

            total_quotes_read += len(quotes)

            # Retain each quote along with its batch metadata

            for quote in quotes:

                raw_quotes.append(
                    (quote, batch_data, file_path.name)
                )

            files_processed += 1

            logging.info(
                "File successfully read: %s | Quotes found: %d",
                file_path.name,
                len(quotes)
            )

        except Exception:

            failed_files += 1

            logging.exception(
                "FAILED: Unable to read file: %s",
                file_path.name
            )

    logging.info(
        "Total raw quote records collected: %d",
        len(raw_quotes)
    )

    return (
        raw_quotes,
        total_quotes_read,
        files_processed,
        failed_files
    )


# ============================================================
# STEP 3: EXTRACT METADATA AND FLATTEN NESTED JSON RECORDS
# ============================================================

def flatten_quote(quote, batch_data):

    supplier = quote.get("supplier") or {}
    material = quote.get("material") or {}
    pricing = quote.get("pricing") or {}

    # Ensure nested values are dictionaries

    if not isinstance(supplier, dict):
        supplier = {}

    if not isinstance(material, dict):
        material = {}

    if not isinstance(pricing, dict):
        pricing = {}

    flattened_record = {

        # Quote-level attributes
        "quote_id": quote.get("quote_id"),

        # Batch-level metadata
        "batch_id": batch_data.get("batch_id"),
        "submitted_by": batch_data.get("submitted_by"),

        # Supplier attributes
        "supplier_id": supplier.get("id"),
        "supplier_name": supplier.get("name"),
        "supplier_country": supplier.get("country") or "UNKNOWN",

        # Material attributes
        "material_code": material.get("code"),
        "material_name": material.get("name"),

        # Pricing attributes
        "unit_price_usd": float(
            pricing.get("unit_price_usd", 0.0)
        ),

        "min_order_qty": int(
            pricing.get("min_order_qty", 0)
        ),

        "discount_pct": float(
            pricing.get("discount_pct", 0.0)
        ),

        # Validity information
        "valid_until": quote.get("valid_until")
    }

    return flattened_record


def flatten_records(raw_quotes):

    logging.info(
        "STEP 3 STARTED: Extract metadata and flatten nested JSON records"
    )

    flattened_quotes = []
    invalid_quotes = 0

    for quote, batch_data, file_name in raw_quotes:

        try:

            if not isinstance(quote, dict):

                invalid_quotes += 1

                logging.warning(
                    "Invalid quote record skipped from %s",
                    file_name
                )

                continue

            quote_id = quote.get("quote_id")

            logging.info("Flattening quote_id: %s", quote_id)

            flattened_record = flatten_quote(
                quote,
                batch_data
            )

            flattened_quotes.append(flattened_record)

            logging.info(
                "Successfully flattened quote_id: %s",
                quote_id
            )

        except (ValueError, TypeError, OverflowError):

            invalid_quotes += 1

            logging.exception(
                "STEP 3 FAILED: Unable to flatten quote from %s",
                file_name
            )

    logging.info(
        "Total flattened records: %d",
        len(flattened_quotes)
    )

    logging.info(
        "STEP 3 COMPLETED: Metadata extraction and flattening"
    )

    return flattened_quotes, invalid_quotes


# ============================================================
# STEP 4: IDENTIFY AND REMOVE CROSS-FILE DUPLICATES
# ============================================================

def deduplicate_quotes(flattened_quotes):

    logging.info(
        "STEP 4 STARTED: Identify and eliminate duplicate quote records"
    )

    # In-memory tracking set for unique quote IDs

    seen_quote_ids = set()

    unique_quotes = []

    duplicates_skipped = 0
    invalid_quotes = 0

    for record in flattened_quotes:

        quote_id = record.get("quote_id")

        # Validate quote ID

        if not quote_id:

            invalid_quotes += 1

            logging.warning(
                "Quote skipped because quote_id is missing"
            )

            continue

        # Check whether quote ID already exists

        if quote_id in seen_quote_ids:

            duplicates_skipped += 1

            logging.warning(
                "Duplicate quote_id skipped: %s",
                quote_id
            )

            continue

        # Track unique quote ID

        seen_quote_ids.add(quote_id)

        unique_quotes.append(record)

        logging.info(
            "Unique quote retained: %s",
            quote_id
        )

    logging.info(
        "STEP 4 COMPLETED: Deduplication completed"
    )

    return unique_quotes, duplicates_skipped, invalid_quotes


# ============================================================
# STEP 5: LOG EXECUTION DETAILS AND DISPLAY SUMMARY
# ============================================================

def main():

    try:

        initialize_logging()

        # Step 2: Discover and read JSON files

        json_files = discover_json_files()

        if not json_files:

            logging.warning(
                "No JSON files found in incoming directory"
            )

        (
            raw_quotes,
            total_quotes_read,
            files_processed,
            failed_files
        ) = read_json_files(json_files)

        # Step 3: Flatten nested JSON records

        flattened_quotes, flattening_invalid = flatten_records(
            raw_quotes
        )

        # Step 4: Deduplicate flattened records

        (
            unique_quotes,
            duplicates_skipped,
            deduplication_invalid
        ) = deduplicate_quotes(flattened_quotes)

        invalid_quotes = (
            flattening_invalid + deduplication_invalid
        )

        # Step 5: Execution summary

        logging.info(
            "STEP 5 STARTED: Generate execution summary"
        )

        logging.info("=" * 60)
        logging.info("EXECUTION SUMMARY")
        logging.info("Files discovered: %d", len(json_files))
        logging.info("Files processed: %d", files_processed)
        logging.info("Files failed: %d", failed_files)
        logging.info("Total quotes read: %d", total_quotes_read)
        logging.info("Total flattened records: %d", len(flattened_quotes))
        logging.info("Duplicates skipped: %d", duplicates_skipped)
        logging.info("Invalid quotes skipped: %d", invalid_quotes)
        logging.info("Unique quotes identified: %d", len(unique_quotes))
        logging.info("=" * 60)

        print("\nJSON processing completed.")
        print("Files discovered:", len(json_files))
        print("Files processed:", files_processed)
        print("Files failed:", failed_files)
        print("Total quotes read:", total_quotes_read)
        print("Total flattened records:", len(flattened_quotes))
        print("Duplicates skipped:", duplicates_skipped)
        print("Invalid quotes:", invalid_quotes)
        print("Unique quotes identified:", len(unique_quotes))

        logging.info(
            "STEP 5 COMPLETED: Execution summary generated"
        )

        # Return unique flattened records for the next pipeline stage

        return unique_quotes

    except Exception:

        logging.exception("PIPELINE EXECUTION FAILED")
        raise

    finally:

        if logging.getLogger().handlers:

            logging.info(
                "%s ended at %s",
                Path(__file__).name,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )


# ============================================================
# START SCRIPT EXECUTION
# ============================================================

if __name__ == "__main__":

    main()
