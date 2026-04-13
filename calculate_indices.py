#!/usr/bin/env python3
"""Bilateral Price Index Calculator using pyindexnum.

Computes bilateral price indices on the same dataset used by calculate_indices.R,
validates results against the R output, and compares calculation times.
"""

import time
import csv
import math
from pathlib import Path

import polars as pl
import pyindexnum
from pyindexnum.utils import standardize_columns

TOLERANCE = 1e-9
DATASET = "performance_price_data.csv"
START_PERIOD = "2024-01"
END_PERIOD = "2024-02"
R_RESULTS_FILE = "price_indices_results.csv"
OUTPUT_FILE = "python_price_indices_results.csv"

INDEX_CONFIG = [
    ("Jevons", pyindexnum.jevons, False),
    ("Carli", pyindexnum.dudot, False),
    ("Dutot", pyindexnum.carli, False),
    ("Fisher", pyindexnum.fisher, True),
    ("Laspeyres", pyindexnum.laspeyres, True),
    ("Paasche", pyindexnum.paasche, True),
    ("Tornqvist", pyindexnum.tornqvist, True),
    ("Walsh", pyindexnum.walsh, True),
]


def preprocess(filepath: str) -> tuple[pl.DataFrame, int]:
    """Load CSV, standardize columns, aggregate to monthly, balance panel."""
    df = pl.read_csv(filepath)

    df = standardize_columns(
        df,
        date_col="time",
        price_col="prices",
        id_col="prodID",
        quantity_col="quantities",
    )

    agg = pyindexnum.aggregate_time(
        df,
        date_col="date",
        price_col="price",
        quantity_col="quantity",
        id_col="product_id",
        agg_type="weighted_arithmetic",
        freq="1mo",
    )

    agg = agg.rename({"aggregated_price": "price", "aggregated_quantity": "quantity"})
    balanced = pyindexnum.remove_unbalanced(agg)

    balanced = balanced.rename({"period": "date"})

    start_dt = pl.lit(START_PERIOD + "-01").str.strptime(pl.Date, "%Y-%m-%d")
    end_dt = pl.lit(END_PERIOD + "-01").str.strptime(pl.Date, "%Y-%m-%d")
    balanced = balanced.filter(
        (pl.col("date") == start_dt) | (pl.col("date") == end_dt)
    )

    num_products = (
        balanced.filter(pl.col("date") == start_dt).select("product_id").n_unique()
    )

    return balanced, num_products


def compute_indices(df: pl.DataFrame, num_products: int) -> list[dict]:
    """Compute all configured indices with timing."""
    df_unweighted = df.select("date", "price", "product_id")
    results = []

    for name, func, needs_quantity in INDEX_CONFIG:
        data = df if needs_quantity else df_unweighted
        t0 = time.perf_counter()
        value = func(data)
        t1 = time.perf_counter()
        elapsed = t1 - t0
        results.append(
            {
                "dataset": DATASET,
                "start_period": START_PERIOD,
                "end_period": END_PERIOD,
                "index_name": name,
                "value": value,
                "time_seconds": elapsed,
                "num_products": num_products,
            }
        )

    return results


def validate_against_r(
    python_results: list[dict],
) -> list[dict]:
    """Load R results and enrich Python results with comparison columns."""
    r_path = Path(R_RESULTS_FILE)
    if not r_path.exists():
        print(f"WARNING: {R_RESULTS_FILE} not found. Skipping validation.")
        for r in python_results:
            r["matches_r"] = "N/A"
            r["python_faster"] = "N/A"
        return python_results

    r_data = {}
    with open(r_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row["index_name"].strip()
            r_data[key] = {
                "value": float(row["value"]),
                "time_seconds": float(row["time_seconds"]),
            }

    for r in python_results:
        name = r["index_name"]
        if name in r_data:
            r_val = r_data[name]["value"]
            r_time = r_data[name]["time_seconds"]
            py_rounded = round(r["value"], 7)
            r["matches_r"] = str(abs(py_rounded - r_val) < TOLERANCE)
            r["python_faster"] = str(r["time_seconds"] < r_time)
        else:
            r["matches_r"] = "no_r_result"
            r["python_faster"] = "no_r_result"

    return python_results


def save_csv(results: list[dict]) -> None:
    """Write results to CSV."""
    fieldnames = [
        "dataset",
        "start_period",
        "end_period",
        "index_name",
        "value",
        "time_seconds",
        "num_products",
        "matches_r",
        "python_faster",
    ]
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            out = dict(row)
            out["value"] = f"{out['value']:.7f}"
            out["time_seconds"] = f"{out['time_seconds']:.4f}"
            writer.writerow(out)


def print_summary(results: list[dict]) -> None:
    """Print a concise validation summary."""
    r_path = Path(R_RESULTS_FILE)
    r_data = {}
    if r_path.exists():
        with open(r_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                r_data[row["index_name"].strip()] = {
                    "value": float(row["value"]),
                    "time_seconds": float(row["time_seconds"]),
                }

    print("\n========================================")
    print("  BILATERAL PRICE INDEX RESULTS (Python)")
    print("========================================\n")
    print(
        f"  [{DATASET}  {START_PERIOD} -> {END_PERIOD}  products: {results[0]['num_products']}]\n"
    )

    match_count = 0
    py_faster_count = 0
    py_total_time = 0.0
    r_total_time = 0.0
    comparable = 0

    print(
        f"  {'Index':<25s} {'Value':>15s}  {'Time(s)':>10s}  {'Matches R':>10s}  {'Py Faster':>10s}"
    )
    print("  " + "-" * 80)

    for r in results:
        name = r["index_name"]
        matches = r["matches_r"]
        faster = r["python_faster"]
        val_str = f"{r['value']:.7f}"
        time_str = f"{r['time_seconds']:.4f}"

        print(
            f"  {name:<25s} {val_str:>15s}  {time_str:>10s}  {matches:>10s}  {faster:>10s}"
        )

        if matches == "True":
            match_count += 1
        if faster == "True":
            py_faster_count += 1
        if name in r_data:
            py_total_time += r["time_seconds"]
            r_total_time += r_data[name]["time_seconds"]
            comparable += 1

    print("\n========================================")
    print("  VALIDATION SUMMARY")
    print("========================================")
    print(f"  Indices computed (Python): {len(results)}")
    print(f"  Indices available in R:    {len(r_data)}")
    print(f"  Matched R values (<{TOLERANCE}):  {match_count}/{len(results)}")

    r_only = set(r_data.keys()) - {r["index_name"] for r in results}
    if r_only:
        print(
            f"  R indices not in pyindexnum ({len(r_only)}): {', '.join(sorted(r_only))}"
        )

    if comparable > 0:
        avg_py = py_total_time / comparable
        avg_r = r_total_time / comparable
        ratio = avg_py / avg_r if avg_r > 0 else float("inf")
        print(f"\n  Avg Python time: {avg_py:.4f}s")
        print(f"  Avg R time:      {avg_r:.4f}s")
        print(f"  Python/R ratio:  {ratio:.2f}x")
        if ratio < 1.0:
            print(f"  -> Python is faster on average")
        else:
            print(f"  -> R is faster on average")
        print(f"  Python faster in {py_faster_count}/{comparable} comparisons")

    print(f"\n  Output: {OUTPUT_FILE}")
    print("========================================\n")


def main() -> None:
    print(f"Loading and preprocessing {DATASET}...")
    df, num_products = preprocess(DATASET)
    print(f"  Products after balancing: {num_products}")

    print("Computing indices...")
    results = compute_indices(df, num_products)

    print("Validating against R results...")
    results = validate_against_r(results)

    save_csv(results)
    print_summary(results)


if __name__ == "__main__":
    main()
