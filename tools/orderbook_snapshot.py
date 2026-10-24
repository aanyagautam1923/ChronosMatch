"""Export a ChronosMatch order-book snapshot to JSON."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def export_snapshot(snapshot, output_path):
    """Write a snapshot dictionary to a JSON file."""
    if not isinstance(snapshot, dict):
        raise TypeError("Snapshot must be a dictionary.")

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    document = {
        "project": "ChronosMatch",
        "format_version": 1,
        "exported_at_utc": datetime.now(timezone.utc).isoformat(),
        "snapshot": snapshot,
    }

    destination.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return destination


def main():
    parser = argparse.ArgumentParser(
        description="Export a supplied order-book snapshot as JSON."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to a JSON file containing an order-book snapshot dictionary.",
    )
    parser.add_argument(
        "--output",
        default="data/exports/orderbook_snapshot.json",
        help="Destination JSON path.",
    )
    args = parser.parse_args()

    source = Path(args.input)
    if not source.is_file():
        parser.error(f"Input file does not exist: {source}")

    try:
        snapshot = json.loads(source.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as error:
        parser.error(f"Input is not valid JSON: {error}")

    if not isinstance(snapshot, dict):
        parser.error("Input JSON must contain an object/dictionary.")

    destination = export_snapshot(snapshot, args.output)
    print(f"Snapshot exported successfully: {destination}")


if __name__ == "__main__":
    main()
